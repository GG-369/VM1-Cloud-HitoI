# proveedores-api

Microservicio de Proveedores. Python + FastAPI + SQLAlchemy, MySQL (`proveedores_db` en VM3).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/proveedores` | Crea un proveedor |
| GET | `/api/proveedores` | Lista proveedores |
| GET | `/api/proveedores/{id}` | Detalle de un proveedor |
| POST | `/api/proveedores/tiempos-entrega` | Registra un tiempo de entrega proveedor↔producto |
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
