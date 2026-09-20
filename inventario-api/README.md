# inventario-api

Microservicio de Inventario. Python + FastAPI + SQLAlchemy, MySQL (`inventario_db` en VM3).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/inventario/productos` | Crea un producto |
| GET | `/api/inventario/productos` | Lista productos (paginado: `skip`, `limit`) |
| GET | `/api/inventario/productos/{id}` | Detalle de un producto |
| PATCH | `/api/inventario/productos/{id}` | Actualiza parcialmente un producto (no edita el stock; 409 si el SKU ya existe) |
| DELETE | `/api/inventario/productos/{id}` | Elimina un producto (409 si tiene movimientos registrados) |
| GET | `/api/inventario/stock/{producto_id}` | Stock actual y mínimo de un producto |
| POST | `/api/inventario/movimientos` | Registra un movimiento y actualiza el stock de forma transaccional. `entrada`/`salida`: `cantidad` > 0. `ajuste`: `cantidad` es el stock resultante del conteo físico (>= 0, admite 0) |
| GET | `/api/inventario/movimientos` | Lista movimientos (filtros: `producto_id`, `tipo_movimiento`; paginado) |
| GET | `/api/inventario/movimientos/{id}` | Detalle de un movimiento |
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
