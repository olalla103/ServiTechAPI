from fastapi import APIRouter, HTTPException
from typing import List
from models.factura_producto import FacturaProductoDB, FacturaProductoCreate, FacturaProductoUpdate
from repository.handler_factura_producto import (
    get_productos_de_factura,
    get_factura_producto_by_id,
    insertar_factura_producto,
    actualizar_factura_producto,
    eliminar_factura_producto,
)

router = APIRouter()

# Listar todos los productos de una factura
@router.get("/factura/{factura_id}", response_model=List[FacturaProductoDB])
def listar_productos_de_factura(factura_id: int):
    return get_productos_de_factura(factura_id)

# Obtener una relación factura-producto por su id único
@router.get("/{id}", response_model=FacturaProductoDB)
def obtener_factura_producto(id: int):
    relacion = get_factura_producto_by_id(id)
    if not relacion:
        raise HTTPException(status_code=404, detail="Factura-producto no encontrada")
    return relacion

# Crear una nueva relación factura-producto
@router.post("/", response_model=FacturaProductoDB)
def crear_factura_producto(datos: FacturaProductoCreate):
    nueva_id = insertar_factura_producto(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo añadir el producto a la factura")
    return get_factura_producto_by_id(nueva_id)

# Editar la cantidad de productos usados en la factura
@router.patch("/{id}")
def editar_cantidad_factura_producto(id: int, datos: FacturaProductoUpdate):
    if datos.cantidad is None:
        raise HTTPException(status_code=400, detail="Debes indicar la cantidad")
    ok = actualizar_factura_producto(id, datos.cantidad)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la cantidad")
    return {"ok": True}


# Eliminar una relación factura-producto
@router.delete("/{id}")
def borrar_factura_producto(id: int):
    ok = eliminar_factura_producto(id)
    if not ok:
        raise HTTPException(status_code=404, detail="No se pudo eliminar la relación factura-producto")
    return {"ok": True}
