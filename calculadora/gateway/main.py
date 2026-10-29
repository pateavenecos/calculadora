"""API Gateway: único punto de entrada REST para el frontend.

Recibe /api/<servicio>/<ruta> y reenvía la petición al microservicio correspondiente.
"""
import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

SERVICIOS = {
    "circulo": os.getenv("CIRCULO_URL", "http://localhost:8001"),
    "cuadrado": os.getenv("CUADRADO_URL", "http://localhost:8002"),
    "triangulo": os.getenv("TRIANGULO_URL", "http://localhost:8003"),
    "potencia": os.getenv("POTENCIA_URL", "http://localhost:8004"),
    "ecuacion_cuadratica": os.getenv("ECUACION_URL", "http://localhost:8005"),
}

app = FastAPI(title="API Gateway - Calculadora")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def raiz():
    return {"gateway": "ok", "servicios": list(SERVICIOS)}


@app.get("/health")
async def health():
    estado = {}
    async with httpx.AsyncClient(timeout=3) as client:
        for nombre, url in SERVICIOS.items():
            try:
                r = await client.get(f"{url}/health")
                estado[nombre] = "ok" if r.status_code == 200 else f"error {r.status_code}"
            except httpx.HTTPError:
                estado[nombre] = "caído"
    return estado


@app.api_route("/api/{servicio}/{ruta:path}", methods=["GET", "POST"])
async def proxy(servicio: str, ruta: str, request: Request):
    base = SERVICIOS.get(servicio)
    if base is None:
        return Response(
            content='{"detail":"Servicio no encontrado"}',
            status_code=404,
            media_type="application/json",
        )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.request(
                request.method,
                f"{base}/{ruta}",
                params=request.query_params,
                content=await request.body(),
                headers={"content-type": request.headers.get("content-type", "application/json")},
            )
    except httpx.HTTPError:
        return Response(
            content='{"detail":"El microservicio no responde"}',
            status_code=503,
            media_type="application/json",
        )
    return Response(
        content=r.content,
        status_code=r.status_code,
        media_type=r.headers.get("content-type", "application/json"),
    )
