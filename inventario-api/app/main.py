from fastapi import FastAPI

from . import models
from .db import Base, engine
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventario API",
    description="Microservicio de inventario — Bodega Inteligente (CS2032)",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "inventario-api"}
