from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProveedorCreate(BaseModel):
    nombre: str
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
    dias_entrega_promedio: int
    dias_entrega_min: int
    dias_entrega_max: int


class TiempoEntregaOut(BaseModel):
    producto_id: int
    proveedor_id: int
    proveedor_nombre: str
    dias_entrega_promedio: int
    dias_entrega_min: int
    dias_entrega_max: int
