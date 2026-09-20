# proveedores-api

Microservicio de Proveedores. Python + FastAPI + SQLAlchemy, MySQL (`proveedores_db` en VM3).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/proveedores` | Crea un proveedor |
| GET | `/api/proveedores` | Lista proveedores (paginado: `skip`, `limit`) |
| GET | `/api/proveedores/{id}` | Detalle de un proveedor |
| PATCH | `/api/proveedores/{id}` | Actualiza parcialmente un proveedor |
| DELETE | `/api/proveedores/{id}` | Elimina un proveedor (409 si tiene tiempos de entrega registrados) |
| POST | `/api/proveedores/tiempos-entrega` | Registra un tiempo de entrega proveedor↔producto (exige `min <= promedio <= max`; 409 si ya existe para ese proveedor y producto) |
| GET | `/api/proveedores/tiempos-entrega` | Lista tiempos de entrega (filtros: `proveedor_id`, `producto_id`; paginado) |
| GET | `/api/proveedores/tiempos-entrega/{id}` | Detalle de un tiempo de entrega |
| PATCH | `/api/proveedores/tiempos-entrega/{id}` | Actualiza parcialmente un tiempo de entrega |
| DELETE | `/api/proveedores/tiempos-entrega/{id}` | Elimina un tiempo de entrega |
| GET | `/api/proveedores/producto/{producto_id}/tiempo-entrega` | Tiempo de entrega (mejor proveedor disponible) para un producto — usado por `prediccion-api` y `alertas-api` |
| GET | `/health` | Healthcheck |

Swagger-UI automático en `/docs`.

## Variables de entorno

Ver `.env.example`. `DB_HOST` debe apuntar a la IP privada de VM3 en despliegue real.

## Correr localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```
