from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TipoMovimientoEnum(str, Enum):
    entrada = "entrada"
    salida = "salida"
    ajuste = "ajuste"


class ProductoCreate(BaseModel):
    sku: str
    nombre: str
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = "unidad"
    stock_actual: int = 0
    stock_minimo: int = 0
    precio_unitario: Decimal = Decimal("0.00")


class ProductoUpdate(BaseModel):
    """Actualización parcial. El stock no se edita aquí: cambia solo vía movimientos."""

    sku: Optional[str] = None
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = None
    stock_minimo: Optional[int] = Field(default=None, ge=0)
    precio_unitario: Optional[Decimal] = Field(default=None, ge=0)


class ProductoOut(BaseModel):
    id: int
    sku: str
    nombre: str
    categoria: Optional[str]
    unidad_medida: Optional[str]
    stock_actual: int
    stock_minimo: int
    precio_unitario: Decimal
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class StockOut(BaseModel):
    producto_id: int
    sku: str
    nombre: str
    stock_actual: int
    stock_minimo: int
    en_riesgo: bool = Field(description="True si stock_actual <= stock_minimo")


class MovimientoCreate(BaseModel):
    producto_id: int
    tipo_movimiento: TipoMovimientoEnum
    cantidad: int = Field(gt=0, description="Cantidad del movimiento, siempre positiva")
    motivo: Optional[str] = None
    usuario: Optional[str] = None


class MovimientoOut(BaseModel):
    id: int
    producto_id: int
    tipo_movimiento: TipoMovimientoEnum
    cantidad: int
    fecha_movimiento: Optional[datetime]
    motivo: Optional[str]
    usuario: Optional[str]

    class Config:
        from_attributes = True
