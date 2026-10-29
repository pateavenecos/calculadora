FROM python:3.12-slim

WORKDIR /app
COPY services/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/ /app/
COPY gateway/ /app/gateway/

# Se define en docker-compose: p. ej. "circulo.main:app" o "gateway.main:app"
ARG MODULO
ENV MODULO=${MODULO}
CMD ["sh", "-c", "uvicorn $MODULO --host 0.0.0.0 --port 8000"]
