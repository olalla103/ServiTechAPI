import os
import tempfile
import traceback

from fastapi import APIRouter, HTTPException
from typing import List

from fastapi.responses import Response


from models.facturas import FacturaDB, FacturaCreate, FacturaUpdate, FacturaConIncidencia
from repository.handler_factura import (
    get_all_facturas,
    get_factura_by_id,
    insertar_factura,
    actualizar_factura,
    eliminar_factura, get_facturas_por_tecnico, get_facturas_por_incidencia,
    get_facturas_resueltas_por_tecnico, crear_factura_backend, get_factura_por_incidencia_id, generar_pdf_factura,
)
from repository.handler_usuario import get_usuario_by_id

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

@router.get("/por-incidencia/{incidencia_id}")
def get_factura_por_incidencia(incidencia_id: int):
    factura = get_factura_por_incidencia_id(incidencia_id)
    if not factura:
        # Puede devolver None si no hay factura aún
        return None
    return factura

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

@router.get("/descargar/{numero_factura}")
def descargar_factura(numero_factura: int):
    # 1. Obtén la factura, el cliente y el técnico
    factura = get_factura_by_id(numero_factura)
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    cliente = get_usuario_by_id(factura.cliente_id)
    tecnico = get_usuario_by_id(factura.tecnico_id)

    # 2. Usa un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        ruta_pdf = temp_pdf.name
    try:
        # 3. Genera el PDF en esa ruta
        generar_pdf_factura(factura, cliente, tecnico, ruta_salida=ruta_pdf)

        # 4. Lee el PDF generado
        with open(ruta_pdf, "rb") as f:
            pdf_bytes = f.read()

        # 5. Devuelve el PDF como attachment
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="factura{numero_factura}.pdf"'
            }
        )
    finally:
        # Borra el archivo temporal (importante)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

@router.get("/incidencia/{incidencia_id}", response_model=List[FacturaConIncidencia])
def listar_facturas_por_incidencia(incidencia_id: int):
    """
    Devuelve todas las facturas asociadas a una incidencia específica.
    """
    return get_facturas_por_incidencia(incidencia_id)


@router.get("/tecnico/{tecnico_id}", response_model=List[FacturaConIncidencia])
def listar_facturas_tecnico(tecnico_id: int):
    return get_facturas_por_tecnico(tecnico_id)

# =========================
# === CREACIÓN (POST) =====
# =========================

# Crear una nueva factura
# @router.post("/", response_model=FacturaDB)
# def crear_factura(datos: FacturaCreate):
#     """
#     Crea una factura con sus productos asociados.
#     Calcula y actualiza automáticamente la cantidad adicional.
#     """
#     # 1. Insertar la factura principal (sin cantidad_adicional)
#     nueva_id = insertar_factura(datos.model_dump(exclude={'productos'}))  # NO envíes 'productos'
#     if not nueva_id:
#         raise HTTPException(status_code=400, detail="No se pudo crear la factura")
#
#     # 2. Insertar los productos, si llegan
#     if datos.productos:
#         for prod in datos.productos:
#             insertar_factura_producto({
#                 "factura_id": nueva_id,
#                 "producto_id": prod.producto_id,
#                 "cantidad": prod.cantidad
#             })
#         # 3. Recalcular la cantidad adicional
#         actualizar_cantidad_adicional_en_factura(nueva_id)
#
#     # 4. Devuelve la factura completa (ya con cantidad_adicional recalculada)
#     return get_factura_by_id(nueva_id)

@router.get("/resueltas/tecnico/{tecnico_id}", response_model=List[FacturaConIncidencia])
def listar_facturas_resueltas_tecnico(tecnico_id: int):
    """
    Devuelve todas las facturas de incidencias resueltas asociadas a un técnico.
    """
    return get_facturas_resueltas_por_tecnico(tecnico_id)


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


from datetime import datetime

@router.post("/", response_model=FacturaDB)
def crear_factura(factura: FacturaCreate):
    print("LLEGA FACTURA AL ENDPOINT:", factura)
    try:
        nueva_id = crear_factura_backend(factura.model_dump())
        if not nueva_id:
            raise HTTPException(status_code=400, detail="Error al crear factura")
        print("NUEVA ID FACTURA:", nueva_id)
        result = get_factura_by_id(nueva_id)
        print("RESULTADO FACTURA:", result)
        return result
    except Exception as e:
        print("ERROR EN CREAR_FACTURA:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
