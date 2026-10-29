from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from common import db

SERVICIO = "triangulo"
app = FastAPI(title="Microservicio Triángulo")
db.init_db()


class TrianguloIn(BaseModel):
    base: float = Field(..., gt=0)
    altura: float = Field(..., gt=0)
    lado_a: float = Field(..., gt=0, description="Segundo lado")
    lado_b: float = Field(..., gt=0, description="Tercer lado")


@app.get("/health")
def health():
    return {"servicio": SERVICIO, "estado": "ok"}


@app.post("/calcular")
def calcular(datos: TrianguloIn):
    # Desigualdad triangular
    a, b, c = datos.base, datos.lado_a, datos.lado_b
    if a + b <= c or a + c <= b or b + c <= a:
        raise HTTPException(status_code=422, detail="Los lados no forman un triángulo válido")
    resultado = {
        "area": round(datos.base * datos.altura / 2, 4),
        "perimetro": round(a + b + c, 4),
    }
    id_ = db.guardar(SERVICIO, datos.model_dump(), resultado)
    return {"id": id_, "servicio": SERVICIO, "entrada": datos.model_dump(), "resultado": resultado}


@app.get("/historial")
def historial(limite: int = 20):
    return db.historial(SERVICIO, limite)
