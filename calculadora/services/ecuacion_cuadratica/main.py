import cmath
import math

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common import db

SERVICIO = "ecuacion_cuadratica"
app = FastAPI(title="Microservicio Ecuación Cuadrática")
db.init_db()


class EcuacionIn(BaseModel):
    a: float
    b: float
    c: float


@app.get("/health")
def health():
    return {"servicio": SERVICIO, "estado": "ok"}


def _fmt(z: complex):
    """Devuelve número real si no tiene parte imaginaria, o texto 'x + yi'."""
    real = round(z.real, 6) + 0.0  # "+ 0.0" evita mostrar -0.0
    if abs(z.imag) < 1e-12:
        return real
    signo = "+" if z.imag >= 0 else "-"
    return f"{real} {signo} {round(abs(z.imag), 6)}i"


@app.post("/calcular")
def calcular(datos: EcuacionIn):
    if datos.a == 0:
        raise HTTPException(status_code=422, detail="'a' no puede ser 0 (no sería una ecuación cuadrática)")

    disc = datos.b**2 - 4 * datos.a * datos.c
    raiz = cmath.sqrt(disc)
    x1 = (-datos.b + raiz) / (2 * datos.a)
    x2 = (-datos.b - raiz) / (2 * datos.a)

    if disc > 0:
        tipo = "dos raíces reales distintas"
    elif math.isclose(disc, 0, abs_tol=1e-12):
        tipo = "una raíz real doble"
    else:
        tipo = "dos raíces complejas conjugadas"

    resultado = {
        "discriminante": round(disc, 6),
        "tipo": tipo,
        "x1": _fmt(x1),
        "x2": _fmt(x2),
    }
    id_ = db.guardar(SERVICIO, datos.model_dump(), resultado)
    return {"id": id_, "servicio": SERVICIO, "entrada": datos.model_dump(), "resultado": resultado}


@app.get("/historial")
def historial(limite: int = 20):
    return db.historial(SERVICIO, limite)
