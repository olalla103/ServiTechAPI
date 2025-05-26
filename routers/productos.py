from fastapi import APIRouter, HTTPException
from typing import List
from models.productos import ProductoDB, ProductoCreate, ProductoUpdate
from repository.handler_producto import (
    get_all_productos,
    get_producto_by_id,
    insertar_producto,
    actualizar_producto,
    eliminar_producto,
)

router = APIRouter()

# Crear un producto
@router.post("/", response_model=ProductoDB)
def crear_producto(datos: ProductoCreate):
    nueva_id = insertar_producto(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo crear el producto")
    return get_producto_by_id(nueva_id)


# Listar todos los productos
@router.get("/", response_model=List[ProductoDB])
def listar_productos():
    return get_all_productos()

# Obtener producto por id
@router.get("/{producto_id}", response_model=ProductoDB)
def obtener_producto(producto_id: int):
    producto = get_producto_by_id(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# Editar producto
@router.patch("/{producto_id}")
def editar_producto(producto_id: int, datos: ProductoUpdate):
    campos = datos.model_dump(exclude_unset=True)
    ok = actualizar_producto(producto_id, campos)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el producto")
    return {"ok": True}

# Eliminar producto
@router.delete("/{producto_id}")
def borrar_producto(producto_id: int):
    ok = eliminar_producto(producto_id)
    if not ok:
        raise HTTPException(status_code=404, detail="No se pudo eliminar el producto")
    return {"ok": True}

