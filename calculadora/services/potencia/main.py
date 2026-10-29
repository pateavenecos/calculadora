from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common import db

SERVICIO = "potencia"
app = FastAPI(title="Microservicio Potencia")
db.init_db()


class PotenciaIn(BaseModel):
    base: float
    exponente: float


@app.get("/health")
def health():
    return {"servicio": SERVICIO, "estado": "ok"}


@app.post("/calcular")
def calcular(datos: PotenciaIn):
    try:
        valor = datos.base**datos.exponente
        if isinstance(valor, complex):
            raise ValueError("El resultado no es un número real")
        if valor in (float("inf"), float("-inf")):
            raise OverflowError
    except ZeroDivisionError:
        raise HTTPException(status_code=422, detail="0 elevado a un exponente negativo no está definido")
    except OverflowError:
        raise HTTPException(status_code=422, detail="El resultado es demasiado grande")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    resultado = {"resultado": round(valor, 6)}
    id_ = db.guardar(SERVICIO, datos.model_dump(), resultado)
    return {"id": id_, "servicio": SERVICIO, "entrada": datos.model_dump(), "resultado": resultado}


@app.get("/historial")
def historial(limite: int = 20):
    return db.historial(SERVICIO, limite)
