from fastapi import APIRouter, HTTPException
from typing import List

from models.factura_producto import FacturaProductoDB, FacturaProductoCreate
from models.facturas import FacturaDB, FacturaCreate, FacturaUpdate
from repository.handler_factura import (
    get_all_facturas,
    get_factura_by_id,
    insertar_factura,
    actualizar_factura,
    eliminar_factura, actualizar_cantidad_adicional_en_factura,
)
from repository.handler_factura_producto import insertar_factura_producto

router = APIRouter()

# ======================
# === CONSULTAS (GET) ===
# ======================

# Listar todas las facturas
@router.get("/", response_model=List[FacturaDB])
def listar_facturas():
    """
    Devuelve una lista con todas las facturas registradas.
    """
    return get_all_facturas()

# Obtener una factura concreta por su número
@router.get("/{numero_factura}", response_model=FacturaDB)
def obtener_factura(numero_factura: int):
    """
    Devuelve los datos de una factura por su número identificador.
    Lanza 404 si no se encuentra.
    """
    factura = get_factura_by_id(numero_factura)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return factura

# =========================
# === CREACIÓN (POST) =====
# =========================

# Crear una nueva factura
@router.post("/", response_model=FacturaDB)
def crear_factura(datos: FacturaCreate):
    """
    Crea una factura a partir de los datos proporcionados en el body.
    Devuelve la factura recién creada.
    Lanza 400 si hay error de inserción.
    """
    nueva_id = insertar_factura(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo crear la factura")
    return get_factura_by_id(nueva_id)

# ==============================
# === EDICIÓN (PATCH) ==========
# ==============================

# Editar una factura existente
@router.patch("/{numero_factura}")
def editar_factura(numero_factura: int, datos: FacturaUpdate):
    """
    Actualiza los campos especificados de la factura cuyo número coincide.
    Solo actualiza los campos presentes en el body.
    Lanza 400 si no se pudo actualizar.
    """
    campos = datos.model_dump(exclude_unset=True)
    ok = actualizar_factura(numero_factura, campos)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la factura")
    return {"ok": True}

# ==============================
# === ELIMINACIÓN (DELETE) =====
# ==============================

# Eliminar una factura por su número
@router.delete("/{numero_factura}")
def borrar_factura(numero_factura: int):
    """
    Elimina la factura indicada por su número identificador.
    Devuelve ok si se elimina, o 404 si no existe o no se pudo borrar.
    """
    ok = eliminar_factura(numero_factura)
    if not ok:
        raise HTTPException(status_code=404, detail="No se pudo eliminar la factura")
    return {"ok": True}


def get_factura_producto_by_id(nueva_id):
    pass


@router.post("/", response_model=FacturaProductoDB)
def crear_factura_producto(datos: FacturaProductoCreate):
    nueva_id = insertar_factura_producto(datos.model_dump())
    if not nueva_id:
        raise HTTPException(status_code=400, detail="No se pudo añadir el producto a la factura")
    # Calcula y actualiza la cantidad adicional de la factura
    actualizar_cantidad_adicional_en_factura(datos.factura_id)
    return get_factura_producto_by_id(nueva_id)
