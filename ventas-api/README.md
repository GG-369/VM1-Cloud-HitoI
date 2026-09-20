# ventas-api

Microservicio de Ventas. Java 17 + Spring Boot 3 + Spring Data JPA, PostgreSQL (`ventas_db` en VM3).

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/ventas` | Registra una venta diaria (calcula `total` en el servidor) |
| GET | `/api/ventas` | Lista ventas (filtros: `productoId`, `desde`, `hasta` en `YYYY-MM-DD`; paginado: `page`, `size`, máx. 200) |
| GET | `/api/ventas/{id}` | Detalle de una venta |
| PATCH | `/api/ventas/{id}` | Actualiza parcialmente una venta (recalcula `total`; los campos omitidos/nulos no cambian) |
| DELETE | `/api/ventas/{id}` | Elimina una venta |
| GET | `/api/ventas/producto/{productoId}?dias=N` | Historial de ventas por producto, opcionalmente acotado a los últimos N días |
| POST | `/api/ventas/pedidos-proveedor` | Registra un pedido a proveedor |
| GET | `/api/ventas/pedidos-proveedor` | Lista pedidos (filtros: `productoId`, `proveedorId`, `estado`; paginado: `page`, `size`) |
| GET | `/api/ventas/pedidos-proveedor/detalle/{id}` | Detalle de un pedido por su id |
| GET | `/api/ventas/pedidos-proveedor/{productoId}` | Historial de pedidos a proveedor de un producto |
| PATCH | `/api/ventas/pedidos-proveedor/{id}` | Actualiza parcialmente un pedido (los campos omitidos/nulos no cambian) |
| DELETE | `/api/ventas/pedidos-proveedor/{id}` | Elimina un pedido |
| GET | `/health` | Healthcheck |

Los errores de "no encontrado" devuelven 404.

## Documentación interactiva

Swagger-UI en `/swagger-ui.html` (springdoc-openapi), esquema OpenAPI en `/v3/api-docs`.

## Variables de entorno

Ver `.env.example`. `DB_HOST` debe apuntar a la IP privada de VM3 en despliegue real. `spring.jpa.hibernate.ddl-auto=update` crea las tablas automáticamente al arrancar (no hay migraciones formales tipo Flyway/Liquibase en este proyecto).

## Correr localmente

```bash
mvn spring-boot:run
```
