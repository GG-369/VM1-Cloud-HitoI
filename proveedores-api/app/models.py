from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .db import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    contacto = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    tiempos_entrega = relationship("TiempoEntrega", back_populates="proveedor")


class TiempoEntrega(Base):
    __tablename__ = "tiempos_entrega"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)
    producto_id = Column(Integer, nullable=False, index=True)
    dias_entrega_promedio = Column(Integer, nullable=False)
    dias_entrega_min = Column(Integer, nullable=False)
    dias_entrega_max = Column(Integer, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    proveedor = relationship("Proveedor", back_populates="tiempos_entrega")
