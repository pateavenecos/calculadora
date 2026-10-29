from fastapi import FastAPI
from pydantic import BaseModel, Field

from common import db

SERVICIO = "cuadrado"
app = FastAPI(title="Microservicio Cuadrado")
db.init_db()


class CuadradoIn(BaseModel):
    lado: float = Field(..., gt=0, description="Longitud del lado")


@app.get("/health")
def health():
    return {"servicio": SERVICIO, "estado": "ok"}


@app.post("/calcular")
def calcular(datos: CuadradoIn):
    resultado = {
        "area": round(datos.lado**2, 4),
        "perimetro": round(4 * datos.lado, 4),
    }
    id_ = db.guardar(SERVICIO, datos.model_dump(), resultado)
    return {"id": id_, "servicio": SERVICIO, "entrada": datos.model_dump(), "resultado": resultado}


@app.get("/historial")
def historial(limite: int = 20):
    return db.historial(SERVICIO, limite)
