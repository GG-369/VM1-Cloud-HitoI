from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TipoMovimientoEnum(str, Enum):
    entrada = "entrada"
    salida = "salida"
    ajuste = "ajuste"


class ProductoCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=150)
    categoria: Optional[str] = None
    unidad_medida: Optional[str] = "unidad"
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=0, ge=0)
    precio_unitario: Decimal = Field(default=Decimal("0.00"), ge=0)


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
    cantidad: int = Field(
        ge=0,
        description=(
            "Entrada/salida: cantidad a mover (> 0). "
            "Ajuste: stock resultante tras el conteo físico (>= 0, admite 0)."
        ),
    )
    motivo: Optional[str] = None
    usuario: Optional[str] = None

    @model_validator(mode="after")
    def _cantidad_positiva_salvo_ajuste(self):
        if self.tipo_movimiento != TipoMovimientoEnum.ajuste and self.cantidad <= 0:
            raise ValueError("cantidad debe ser mayor que 0 para entradas y salidas")
        return self


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
