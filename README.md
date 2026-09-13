# VM1 — Producción A

Instancia sugerida: **t3.small** (2 vCPU / 2 GB), Ubuntu 22.04, Docker + docker-compose.

Corre 3 de los 6 microservicios del sistema, cada uno con su propia base de datos en VM3:

| Servicio | Lenguaje | Puerto | Base de datos (en VM3) |
|---|---|---|---|
| `inventario-api` | Python (FastAPI) | 8001 | MySQL — `inventario_db` |
| `ventas-api` | Java (Spring Boot) | 8002 | PostgreSQL — `ventas_db` |
| `proveedores-api` | Python (FastAPI) | 8003 | MySQL — `proveedores_db` |

## Cómo levantar

1. Copiar `.env.example` a `.env` dentro de cada subcarpeta de servicio (`inventario-api/.env`, `ventas-api/.env`, `proveedores-api/.env`) y completar `DB_HOST` con la IP privada de VM3 (en local, usar la IP/host del contenedor de VM3 según cómo se integren los compose).
2. Desde esta carpeta:

```bash
docker-compose up --build
```

3. Verificar salud: `curl http://localhost:8001/health`, `:8002/health`, `:8003/health`.
4. Swagger: `http://localhost:8001/docs`, `http://localhost:8002/swagger-ui.html`, `http://localhost:8003/docs`.

## Red y seguridad (despliegue AWS real)

- Subred privada de aplicación, **sin IP pública**.
- Security group: entrada solo desde el Security Group del balanceador de carga (ALB) en los puertos 8001-8003.
- Acceso administrativo vía **AWS SSM Session Manager** — sin puerto 22 (SSH) abierto a internet.
- Salida permitida hacia VM3 (puertos 3306 y 5432) para que los 3 servicios puedan conectarse a sus bases de datos.

## Dueños

Integrante 1 (Inventario), Integrante 3 (Proveedores), Integrante 2 (Ventas).
