from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .db import get_db

router = APIRouter(prefix="/api/proveedores", tags=["proveedores"])


def _tiempo_out(tiempo: models.TiempoEntrega, proveedor_nombre: str) -> schemas.TiempoEntregaOut:
    return schemas.TiempoEntregaOut(
        id=tiempo.id,
        producto_id=tiempo.producto_id,
        proveedor_id=tiempo.proveedor_id,
        proveedor_nombre=proveedor_nombre,
        dias_entrega_promedio=tiempo.dias_entrega_promedio,
        dias_entrega_min=tiempo.dias_entrega_min,
        dias_entrega_max=tiempo.dias_entrega_max,
    )


def _validar_rango_dias(minimo: int, promedio: int, maximo: int):
    if not minimo <= promedio <= maximo:
        raise HTTPException(
            status_code=422,
            detail="Se requiere dias_entrega_min <= dias_entrega_promedio <= dias_entrega_max",
        )


def _obtener_tiempo_o_404(db: Session, tiempo_id: int) -> models.TiempoEntrega:
    tiempo = db.query(models.TiempoEntrega).filter(models.TiempoEntrega.id == tiempo_id).first()
    if not tiempo:
        raise HTTPException(status_code=404, detail="Tiempo de entrega no encontrado")
    return tiempo


# --- Proveedores -----------------------------------------------------------


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


# Las rutas fijas de /tiempos-entrega deben declararse antes de /{proveedor_id},
# de lo contrario GET /tiempos-entrega se interpretaría como un id inválido.


@router.post("/tiempos-entrega", response_model=schemas.TiempoEntregaOut, status_code=201)
def crear_tiempo_entrega(payload: schemas.TiempoEntregaCreate, db: Session = Depends(get_db)):
    proveedor = (
        db.query(models.Proveedor).filter(models.Proveedor.id == payload.proveedor_id).first()
    )
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    _validar_rango_dias(
        payload.dias_entrega_min, payload.dias_entrega_promedio, payload.dias_entrega_max
    )

    tiempo = models.TiempoEntrega(**payload.model_dump())
    db.add(tiempo)
    db.commit()
    db.refresh(tiempo)
    return _tiempo_out(tiempo, proveedor.nombre)


@router.get("/tiempos-entrega", response_model=list[schemas.TiempoEntregaOut])
def listar_tiempos_entrega(
    proveedor_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    limit = min(limit, 200)
    query = db.query(models.TiempoEntrega)
    if proveedor_id is not None:
        query = query.filter(models.TiempoEntrega.proveedor_id == proveedor_id)
    if producto_id is not None:
        query = query.filter(models.TiempoEntrega.producto_id == producto_id)
    tiempos = query.order_by(models.TiempoEntrega.id).offset(skip).limit(limit).all()
    return [_tiempo_out(t, t.proveedor.nombre) for t in tiempos]


@router.get("/tiempos-entrega/{tiempo_id}", response_model=schemas.TiempoEntregaOut)
def obtener_tiempo_entrega(tiempo_id: int, db: Session = Depends(get_db)):
    tiempo = _obtener_tiempo_o_404(db, tiempo_id)
    return _tiempo_out(tiempo, tiempo.proveedor.nombre)


@router.patch("/tiempos-entrega/{tiempo_id}", response_model=schemas.TiempoEntregaOut)
def actualizar_tiempo_entrega(
    tiempo_id: int, payload: schemas.TiempoEntregaUpdate, db: Session = Depends(get_db)
):
    tiempo = _obtener_tiempo_o_404(db, tiempo_id)

    cambios = payload.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        if valor is None:
            raise HTTPException(status_code=422, detail=f"'{campo}' no puede ser nulo")

    _validar_rango_dias(
        cambios.get("dias_entrega_min", tiempo.dias_entrega_min),
        cambios.get("dias_entrega_promedio", tiempo.dias_entrega_promedio),
        cambios.get("dias_entrega_max", tiempo.dias_entrega_max),
    )

    for campo, valor in cambios.items():
        setattr(tiempo, campo, valor)
    db.commit()
    db.refresh(tiempo)
    return _tiempo_out(tiempo, tiempo.proveedor.nombre)


@router.delete("/tiempos-entrega/{tiempo_id}", status_code=204)
def eliminar_tiempo_entrega(tiempo_id: int, db: Session = Depends(get_db)):
    tiempo = _obtener_tiempo_o_404(db, tiempo_id)
    db.delete(tiempo)
    db.commit()
    return Response(status_code=204)


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
    return _tiempo_out(tiempo, proveedor.nombre if proveedor else "desconocido")


@router.get("/{proveedor_id}", response_model=schemas.ProveedorOut)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


@router.patch("/{proveedor_id}", response_model=schemas.ProveedorOut)
def actualizar_proveedor(
    proveedor_id: int, payload: schemas.ProveedorUpdate, db: Session = Depends(get_db)
):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    cambios = payload.model_dump(exclude_unset=True)
    if "nombre" in cambios and not cambios["nombre"]:
        raise HTTPException(status_code=422, detail="'nombre' no puede ser nulo ni vacío")

    for campo, valor in cambios.items():
        setattr(proveedor, campo, valor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.delete("/{proveedor_id}", status_code=204)
def eliminar_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    tiene_tiempos = (
        db.query(models.TiempoEntrega.id)
        .filter(models.TiempoEntrega.proveedor_id == proveedor_id)
        .first()
    )
    if tiene_tiempos:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar: el proveedor tiene tiempos de entrega registrados",
        )

    try:
        db.delete(proveedor)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="No se puede eliminar el proveedor")
    return Response(status_code=204)
