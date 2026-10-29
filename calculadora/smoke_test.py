"""Prueba de humo del sistema completo, solo con la librería estándar de Python.

Uso (con el gateway y los 5 microservicios ya corriendo):
    python smoke_test.py
    python smoke_test.py http://localhost:8000   # otra URL del gateway
"""
import json
import sys
import urllib.error
import urllib.request

GATEWAY = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
fallos = 0


def llamar(metodo, ruta, cuerpo=None):
    data = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(
        GATEWAY + ruta, data=data, method=metodo, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, None
    except Exception as e:
        return 0, str(e)


def check(nombre, ok, detalle=""):
    global fallos
    print(("OK    " if ok else "FALLO "), nombre, "" if ok else f"-> {detalle}")
    if not ok:
        fallos += 1


# 1. Gateway y salud de los servicios
st, body = llamar("GET", "/health")
check("gateway responde /health", st == 200, f"{st} {body}")
if st == 200:
    for nombre, estado in body.items():
        check(f"microservicio '{nombre}' arriba", estado == "ok", estado)

# 2. Cálculos de punta a punta (gateway -> microservicio -> BD)
casos = [
    ("circulo", {"radio": 5}, lambda r: abs(r["area"] - 78.5398) < 1e-3),
    ("cuadrado", {"lado": 4}, lambda r: r["area"] == 16 and r["perimetro"] == 16),
    ("triangulo", {"base": 3, "altura": 4, "lado_a": 4, "lado_b": 5},
     lambda r: r["area"] == 6 and r["perimetro"] == 12),
    ("potencia", {"base": 2, "exponente": 10}, lambda r: r["resultado"] == 1024),
    ("ecuacion_cuadratica", {"a": 1, "b": -3, "c": 2},
     lambda r: {r["x1"], r["x2"]} == {1.0, 2.0}),
]
for servicio, datos, valida in casos:
    st, body = llamar("POST", f"/api/{servicio}/calcular", datos)
    ok = st == 200 and valida(body["resultado"])
    check(f"POST /api/{servicio}/calcular", ok, f"{st} {body}")

    st, hist = llamar("GET", f"/api/{servicio}/historial")
    check(f"GET  /api/{servicio}/historial (se guardó en la BD)",
          st == 200 and isinstance(hist, list) and len(hist) >= 1, f"{st} {hist}")

# 3. Errores controlados
st, _ = llamar("POST", "/api/triangulo/calcular", {"base": 1, "altura": 1, "lado_a": 1, "lado_b": 10})
check("triángulo imposible devuelve 422", st == 422, st)
st, _ = llamar("POST", "/api/ecuacion_cuadratica/calcular", {"a": 0, "b": 1, "c": 1})
check("ecuación con a=0 devuelve 422", st == 422, st)
st, _ = llamar("POST", "/api/inexistente/calcular", {})
check("servicio desconocido devuelve 404", st == 404, st)

print(f"\n{'TODO OK' if fallos == 0 else f'{fallos} prueba(s) fallaron'}")
sys.exit(1 if fallos else 0)
