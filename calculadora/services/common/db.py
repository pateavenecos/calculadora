"""Conexión compartida a la base de datos (una sola BD para todos los microservicios).

Por defecto usa SQLite para poder correr local sin instalar nada.
En docker-compose se define DATABASE_URL apuntando a PostgreSQL.
"""
import json
import os
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./calculadora.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Operacion(Base):
    __tablename__ = "operaciones"

    id = Column(Integer, primary_key=True, index=True)
    servicio = Column(String(50), index=True, nullable=False)
    entrada = Column(Text, nullable=False)
    resultado = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def guardar(servicio: str, entrada: dict, resultado: dict) -> int:
    with SessionLocal() as db:
        op = Operacion(
            servicio=servicio,
            entrada=json.dumps(entrada),
            resultado=json.dumps(resultado),
        )
        db.add(op)
        db.commit()
        db.refresh(op)
        return op.id


def historial(servicio: str, limite: int = 20) -> list[dict]:
    with SessionLocal() as db:
        filas = (
            db.query(Operacion)
            .filter(Operacion.servicio == servicio)
            .order_by(Operacion.id.desc())
            .limit(limite)
            .all()
        )
        return [
            {
                "id": f.id,
                "entrada": json.loads(f.entrada),
                "resultado": json.loads(f.resultado),
                "fecha": f.fecha.isoformat(),
            }
            for f in filas
        ]
