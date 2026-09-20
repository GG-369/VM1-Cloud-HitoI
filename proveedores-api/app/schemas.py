from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProveedorCreate(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class ProveedorUpdate(BaseModel):
    """Actualización parcial. Solo se modifican los campos enviados."""

    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
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
