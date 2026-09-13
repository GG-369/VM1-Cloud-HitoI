from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db

router = APIRouter(prefix="/api/proveedores", tags=["proveedores"])


@router.post("", response_model=schemas.ProveedorOut, status_code=201)
def crear_proveedor(payload: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    proveedor = models.Proveedor(**payload.model_dump())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.get("", response_model=list[schemas.ProveedorOut])
def listar_proveedores(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    limit = min(limit, 200)
    return (
        db.query(models.Proveedor)
        .order_by(models.Proveedor.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{proveedor_id}", response_model=schemas.ProveedorOut)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.post("/tiempos-entrega", response_model=schemas.TiempoEntregaOut, status_code=201)
def crear_tiempo_entrega(payload: schemas.TiempoEntregaCreate, db: Session = Depends(get_db)):
    proveedor = (
        db.query(models.Proveedor).filter(models.Proveedor.id == payload.proveedor_id).first()
    )
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    tiempo = models.TiempoEntrega(**payload.model_dump())
    db.add(tiempo)
    db.commit()
    db.refresh(tiempo)
    return schemas.TiempoEntregaOut(
        producto_id=tiempo.producto_id,
        proveedor_id=proveedor.id,
        proveedor_nombre=proveedor.nombre,
        dias_entrega_promedio=tiempo.dias_entrega_promedio,
        dias_entrega_min=tiempo.dias_entrega_min,
        dias_entrega_max=tiempo.dias_entrega_max,
    )


@router.get("/producto/{producto_id}/tiempo-entrega", response_model=schemas.TiempoEntregaOut)
def tiempo_entrega_por_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Endpoint clave para prediccion-api y alertas-api: entrega el tiempo de
    entrega del proveedor asociado a un producto. Si un producto tiene
    varios proveedores registrados, se toma el de menor dias_entrega_promedio
    (mejor caso disponible para reabastecer).
    """
    tiempo = (
        db.query(models.TiempoEntrega)
        .filter(models.TiempoEntrega.producto_id == producto_id)
        .order_by(models.TiempoEntrega.dias_entrega_promedio.asc())
        .first()
    )
    if not tiempo:
        raise HTTPException(
            status_code=404,
            detail=f"No hay tiempos de entrega registrados para el producto {producto_id}",
        )

    proveedor = (
        db.query(models.Proveedor).filter(models.Proveedor.id == tiempo.proveedor_id).first()
    )
    return schemas.TiempoEntregaOut(
        producto_id=tiempo.producto_id,
        proveedor_id=tiempo.proveedor_id,
        proveedor_nombre=proveedor.nombre if proveedor else "desconocido",
        dias_entrega_promedio=tiempo.dias_entrega_promedio,
        dias_entrega_min=tiempo.dias_entrega_min,
        dias_entrega_max=tiempo.dias_entrega_max,
    )
