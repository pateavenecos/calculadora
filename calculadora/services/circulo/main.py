import math

from fastapi import FastAPI
from pydantic import BaseModel, Field

from common import db

SERVICIO = "circulo"
app = FastAPI(title="Microservicio Círculo")
db.init_db()


class CirculoIn(BaseModel):
    radio: float = Field(..., gt=0, description="Radio del círculo")


@app.get("/health")
def health():
    return {"servicio": SERVICIO, "estado": "ok"}


@app.post("/calcular")
def calcular(datos: CirculoIn):
    resultado = {
        "area": round(math.pi * datos.radio**2, 4),
        "perimetro": round(2 * math.pi * datos.radio, 4),
    }
    id_ = db.guardar(SERVICIO, datos.model_dump(), resultado)
    return {"id": id_, "servicio": SERVICIO, "entrada": datos.model_dump(), "resultado": resultado}


@app.get("/historial")
def historial(limite: int = 20):
    return db.historial(SERVICIO, limite)
