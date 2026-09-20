from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# Validación ligera de formato (sin depender de email-validator).
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class ProveedorCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = Field(default=None, pattern=EMAIL_PATTERN)
    direccion: Optional[str] = None


class ProveedorUpdate(BaseModel):
    """Actualización parcial. Solo se modifican los campos enviados."""

    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = Field(default=None, pattern=EMAIL_PATTERN)
    direccion: Optional[str] = None


class ProveedorOut(BaseModel):
    id: int
    nombre: str
    contacto: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    direccion: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class TiempoEntregaCreate(BaseModel):
    proveedor_id: int
    producto_id: int
    dias_entrega_promedio: int = Field(ge=0)
    dias_entrega_min: int = Field(ge=0)
    dias_entrega_max: int = Field(ge=0)


class TiempoEntregaUpdate(BaseModel):
    """Actualización parcial. Solo se modifican los campos enviados."""

    dias_entrega_promedio: Optional[int] = Field(default=None, ge=0)
    dias_entrega_min: Optional[int] = Field(default=None, ge=0)
    dias_entrega_max: Optional[int] = Field(default=None, ge=0)


class TiempoEntregaOut(BaseModel):
    id: int
    producto_id: int
    proveedor_id: int
    proveedor_nombre: str
    dias_entrega_promedio: int
    dias_entrega_min: int
    dias_entrega_max: int
