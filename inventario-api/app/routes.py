from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db

router = APIRouter(prefix="/api/inventario", tags=["inventario"])


@router.post("/productos", response_model=schemas.ProductoOut, status_code=201)
def crear_producto(payload: schemas.ProductoCreate, db: Session = Depends(get_db)):
    existente = db.query(models.Producto).filter(models.Producto.sku == payload.sku).first()
    if existente:
        raise HTTPException(status_code=409, detail=f"El SKU '{payload.sku}' ya existe")

    producto = models.Producto(**payload.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.get("/productos", response_model=list[schemas.ProductoOut])
def listar_productos(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    limit = min(limit, 200)
    return (
        db.query(models.Producto)
        .order_by(models.Producto.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/productos/{producto_id}", response_model=schemas.ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.get("/stock/{producto_id}", response_model=schemas.StockOut)
def consultar_stock(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return schemas.StockOut(
        producto_id=producto.id,
        sku=producto.sku,
        nombre=producto.nombre,
        stock_actual=producto.stock_actual,
        stock_minimo=producto.stock_minimo,
        en_riesgo=producto.stock_actual <= producto.stock_minimo,
    )


@router.post("/movimientos", response_model=schemas.MovimientoOut, status_code=201)
def registrar_movimiento(payload: schemas.MovimientoCreate, db: Session = Depends(get_db)):
    producto = (
        db.query(models.Producto)
        .filter(models.Producto.id == payload.producto_id)
        .with_for_update()
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if payload.tipo_movimiento == schemas.TipoMovimientoEnum.entrada:
        producto.stock_actual += payload.cantidad
    elif payload.tipo_movimiento == schemas.TipoMovimientoEnum.salida:
        if producto.stock_actual < payload.cantidad:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Stock insuficiente: disponible {producto.stock_actual}, "
                    f"solicitado {payload.cantidad}"
                ),
            )
        producto.stock_actual -= payload.cantidad
    elif payload.tipo_movimiento == schemas.TipoMovimientoEnum.ajuste:
        producto.stock_actual = payload.cantidad

    movimiento = models.MovimientoInventario(
        producto_id=payload.producto_id,
        tipo_movimiento=payload.tipo_movimiento.value,
        cantidad=payload.cantidad,
        motivo=payload.motivo,
        usuario=payload.usuario,
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento
