# Calculadora con microservicios (Python + Angular)

Arquitectura del diagrama de la actividad:

```
Cliente --HTTP--> Frontend (Angular) --REST--> API Gateway --> 5 microservicios --> 1 BD
                                                  |-- Círculo
                                                  |-- Cuadrado
                                                  |-- Triángulo
                                                  |-- Potencia
                                                  |-- Ecuación cuadrática
```

Los 5 microservicios son FastAPI independientes y comparten una sola base de datos
(tabla `operaciones`, con una columna `servicio` que indica quién guardó cada registro).

## Estructura

```
calculadora/
├── docker-compose.yml        # BD + 5 microservicios + gateway
├── Dockerfile                # imagen común (se elige el módulo con MODULO)
├── gateway/main.py           # API Gateway (puerto 8000)
├── services/
│   ├── common/db.py          # conexión y modelo de la BD compartida
│   ├── circulo/main.py
│   ├── cuadrado/main.py
│   ├── triangulo/main.py
│   ├── potencia/main.py
│   └── ecuacion_cuadratica/main.py
└── frontend/                 # Angular 18 (standalone)
```

## Opción 1: todo con Docker (PostgreSQL)

```bash
docker compose up --build
```

El gateway queda en http://localhost:8000 (documentación de cada servicio en su propio `/docs`
si lo expones; el gateway tiene `/health` para ver el estado de todos).

## Opción 2: sin Docker (SQLite, ideal para desarrollar)

Desde la carpeta `services/`, instala dependencias y levanta cada servicio en su puerto:

```bash
cd services
pip install -r requirements.txt

uvicorn circulo.main:app --port 8001 &
uvicorn cuadrado.main:app --port 8002 &
uvicorn triangulo.main:app --port 8003 &
uvicorn potencia.main:app --port 8004 &
uvicorn ecuacion_cuadratica.main:app --port 8005 &
```

En otra terminal, desde la raíz del proyecto, el gateway:

```bash
cd calculadora
uvicorn gateway.main:app --port 8000
```

En Windows (PowerShell) usa una terminal por servicio, o `Start-Process` en lugar de `&`.
Todos los servicios usan por defecto `sqlite:///./calculadora.db`; para que compartan
el mismo archivo, arráncalos todos desde la misma carpeta (`services/`).

## Frontend

```bash
cd frontend
npm install
npm start
```

Abre http://localhost:4200. El frontend habla solo con el gateway (`http://localhost:8000`,
configurado en `src/app/api.service.ts`).

## Endpoints (a través del gateway)

| Servicio | POST `/api/<servicio>/calcular` con | Devuelve |
|---|---|---|
| `circulo` | `{"radio": 5}` | área, perímetro |
| `cuadrado` | `{"lado": 4}` | área, perímetro |
| `triangulo` | `{"base": 3, "altura": 4, "lado_a": 4, "lado_b": 5}` | área, perímetro |
| `potencia` | `{"base": 2, "exponente": 10}` | resultado |
| `ecuacion_cuadratica` | `{"a": 1, "b": -3, "c": 2}` | discriminante, tipo, x1, x2 |

Cada servicio también expone `GET /api/<servicio>/historial` con las últimas operaciones guardadas.

Prueba rápida:

```bash
curl -X POST http://localhost:8000/api/circulo/calcular \
  -H "Content-Type: application/json" -d '{"radio": 5}'
```
