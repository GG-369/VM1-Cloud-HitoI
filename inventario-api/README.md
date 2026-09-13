# inventario-api

Microservicio de Inventario. Python + FastAPI + SQLAlchemy, MySQL (`inventario_db` en VM3).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/inventario/productos` | Crea un producto |
| GET | `/api/inventario/productos` | Lista productos (paginado: `skip`, `limit`) |
| GET | `/api/inventario/productos/{id}` | Detalle de un producto |
| GET | `/api/inventario/stock/{producto_id}` | Stock actual y mínimo de un producto |
| POST | `/api/inventario/movimientos` | Registra un movimiento (entrada/salida/ajuste) y actualiza el stock de forma transaccional |
| GET | `/health` | Healthcheck |

## Documentación interactiva

FastAPI genera Swagger-UI automáticamente en `/docs` (y el esquema OpenAPI en `/openapi.json`) — no hace falta un `swagger.yaml` manual.

## Variables de entorno

Ver `.env.example`. `DB_HOST` debe apuntar a la IP privada de VM3 en despliegue real.

## Correr localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
