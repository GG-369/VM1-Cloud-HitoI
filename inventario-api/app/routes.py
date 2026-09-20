from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
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


@router.patch("/productos/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int, payload: schemas.ProductoUpdate, db: Session = Depends(get_db)
):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    cambios = payload.model_dump(exclude_unset=True)
    for campo in ("sku", "nombre"):
        if campo in cambios and not cambios[campo]:
            raise HTTPException(status_code=422, detail=f"'{campo}' no puede ser nulo ni vacío")
    if "precio_unitario" in cambios and cambios["precio_unitario"] is None:
        raise HTTPException(status_code=422, detail="'precio_unitario' no puede ser nulo")
    if "stock_minimo" in cambios and cambios["stock_minimo"] is None:
        raise HTTPException(status_code=422, detail="'stock_minimo' no puede ser nulo")

    nuevo_sku = cambios.get("sku")
    if nuevo_sku and nuevo_sku != producto.sku:
        duplicado = db.query(models.Producto).filter(models.Producto.sku == nuevo_sku).first()
        if duplicado:
            raise HTTPException(status_code=409, detail=f"El SKU '{nuevo_sku}' ya existe")

    for campo, valor in cambios.items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/productos/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    tiene_movimientos = (
        db.query(models.MovimientoInventario.id)
        .filter(models.MovimientoInventario.producto_id == producto_id)
        .first()
    )
    if tiene_movimientos:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el producto tiene movimientos registrados",
        )

    try:
        db.delete(producto)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar el producto")
    return Response(status_code=204)


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


@router.get("/movimientos", response_model=list[schemas.MovimientoOut])
def listar_movimientos(
    producto_id: Optional[int] = None,
    tipo_movimiento: Optional[schemas.TipoMovimientoEnum] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    limit = min(limit, 200)
    query = db.query(models.MovimientoInventario)
    if producto_id is not None:
        query = query.filter(models.MovimientoInventario.producto_id == producto_id)
    if tipo_movimiento is not None:
        query = query.filter(
            models.MovimientoInventario.tipo_movimiento == tipo_movimiento.value
        )
    return (
        query.order_by(models.MovimientoInventario.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/movimientos/{movimiento_id}", response_model=schemas.MovimientoOut)
def obtener_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    movimiento = (
        db.query(models.MovimientoInventario)
        .filter(models.MovimientoInventario.id == movimiento_id)
        .first()
    )
    if not movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return movimiento
