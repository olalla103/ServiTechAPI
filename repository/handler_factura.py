from datetime import datetime

import pymysql
from models.facturas import FacturaDB, FacturaConIncidencia
from repository.conexion import get_cursor

def insertar_factura(factura):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO facturas
                (fecha_emision, tiempo_total, cantidad_total, cantidad_adicional, IVA, observaciones,
                 tecnico_id, cliente_id, incidencia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                factura["fecha_emision"],
                factura["tiempo_total"],
                factura["cantidad_total"],
                factura["cantidad_adicional"],
                factura["IVA"],
                factura.get("observaciones"),
                factura["tecnico_id"],
                factura["cliente_id"],
                factura["incidencia_id"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar factura: {e}")
        return None

def get_all_facturas():
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                LEFT JOIN incidencias i ON f.incidencia_id = i.id
            """
            cursor.execute(sql)
            facturas = cursor.fetchall()
            return [FacturaDB(**normaliza_factura(factura)) for factura in facturas]
    except Exception as e:
        print(f"Error al recuperar facturas: {e}")
        return []

def get_facturas_por_incidencia(incidencia_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                LEFT JOIN incidencias i ON f.incidencia_id = i.id
                WHERE f.incidencia_id = %s
            """
            cursor.execute(sql, (incidencia_id,))
            facturas = cursor.fetchall()
            return [FacturaConIncidencia(**factura) for factura in facturas]
    except Exception as e:
        print(f"Error al recuperar facturas por incidencia: {e}")
        return []


def calcular_cantidad_adicional(factura_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT SUM(fp.cantidad * p.precio) AS cantidad_adicional
                FROM facturaproducto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql, (factura_id,))
            row = cursor.fetchone()
            return row["cantidad_adicional"] if row and row["cantidad_adicional"] is not None else 0.0
    except Exception as e:
        print(f"Error al calcular cantidad adicional: {e}")
        return 0.0

def actualizar_cantidad_adicional_en_factura(factura_id: int):
    nueva_cantidad = calcular_cantidad_adicional(factura_id)
    try:
        with get_cursor() as cursor:
            sql = "UPDATE facturas SET cantidad_adicional = %s WHERE numero_factura = %s"
            cursor.execute(sql, (nueva_cantidad, factura_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad adicional: {e}")
        return False

from datetime import datetime

from datetime import datetime

def normaliza_factura(factura):
    factura["fecha_emision"] = factura.get("fecha_emision") or datetime.now()
    factura["tiempo_total"] = factura.get("tiempo_total") or 0.0
    factura["cantidad_total"] = factura.get("cantidad_total") or 0.0
    factura["IVA"] = factura.get("IVA") or 21.0
    return factura


def get_facturas_resueltas_por_tecnico(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                JOIN incidencias i ON f.incidencia_id = i.id
                WHERE i.tecnico_id = %s AND i.estado = 'resuelta'
            """
            cursor.execute(sql, (tecnico_id,))
            facturas = cursor.fetchall()

            facturas_clean = []
            for factura in facturas:
                factura = normaliza_factura(factura)
                facturas_clean.append(FacturaConIncidencia(**factura))
            return facturas_clean

    except Exception as e:
        print(f"Error al recuperar facturas resueltas: {e}")
        return []




def get_facturas_por_tecnico(tecnico_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT f.*, i.descripcion AS incidencia_nombre
                FROM facturas f
                LEFT JOIN incidencias i ON f.incidencia_id = i.id
                WHERE f.tecnico_id = %s
            """
            cursor.execute(sql, (tecnico_id,))
            facturas = cursor.fetchall()
            return [FacturaConIncidencia(**factura) for factura in facturas]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar facturas: {e}")
        return []


def get_factura_by_id(numero_factura: int):
    try:
        with get_cursor() as cursor:
            # 1. Saca la factura principal
            sql_factura = "SELECT * FROM facturas WHERE numero_factura = %s"
            cursor.execute(sql_factura, (numero_factura,))
            factura = cursor.fetchone()
            if not factura:
                return None

            # 2. Saca los productos asociados (JOIN bonito)
            sql_productos = """
                SELECT 
                    p.id, 
                    p.nombre, 
                    p.precio AS precio_unitario, 
                    fp.cantidad
                FROM facturaproducto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql_productos, (numero_factura,))
            productos = cursor.fetchall()  # lista de dicts

            # 3. Añade los productos al dict de la factura
            factura["productos"] = productos

            # 4. Calcula y añade el precio adicional
            factura["cantidad_adicional"] = sum(
                (prod["precio_unitario"] or 0) * (prod["cantidad"] or 0) for prod in productos
            )

            # --- Asegúrate de que los campos NUNCA son None ---
            factura["fecha_emision"] = factura.get("fecha_emision") or datetime.now()
            factura["tiempo_total"] = factura.get("tiempo_total") or 0.0
            factura["cantidad_total"] = factura.get("cantidad_total") or 0.0
            factura["IVA"] = factura.get("IVA") or 21.0  # si quieres forzar siempre 21
            # Puedes añadir otros campos por defecto si es necesario

            # 5. Devuelve la factura como objeto Pydantic
            return FacturaDB(**factura)

    except Exception as e:
        print(f"Error al recuperar factura por id: {e}")
        return None

def get_factura_by_tecnico_and_incidencia(tecnico_id: int, incidencia_id: int):
    with get_cursor() as cursor:
        sql = "SELECT * FROM facturas WHERE tecnico_id = %s AND incidencia_id = %s"
        cursor.execute(sql, (tecnico_id, incidencia_id))
        return cursor.fetchone()

def actualizar_cantidad_adicional_en_factura(factura_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                UPDATE facturas SET cantidad_adicional = (
                    SELECT IFNULL(SUM(fp.cantidad * p.precio), 0)
                    FROM facturaproducto fp
                    JOIN productos p ON fp.producto_id = p.id
                    WHERE fp.factura_id = %s
                )
                WHERE numero_factura = %s
            """
            cursor.execute(sql, (factura_id, factura_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad adicional: {e}")
        return False


def actualizar_factura(numero_factura: int, campos: dict):
    if not campos:
        return False
    try:
        with get_cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in campos])
            valores = list(campos.values()) + [numero_factura]
            sql = f"UPDATE facturas SET {set_clause} WHERE numero_factura = %s"
            cursor.execute(sql, valores)
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al actualizar factura: {e}")
        return False

def eliminar_factura(numero_factura: int):
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM facturas WHERE numero_factura = %s"
            cursor.execute(sql, (numero_factura,))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar factura: {e}")
        return False

def calcular_cantidad_adicional(factura_id: int):
    """
    Calcula la cantidad adicional de una factura sumando (cantidad * precio) de todos los productos usados en la factura.
    """
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT SUM(fp.cantidad * p.precio) AS cantidad_adicional
                FROM facturaproducto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql, (factura_id,))
            row = cursor.fetchone()
            return row["cantidad_adicional"] if row and row["cantidad_adicional"] is not None else 0.0
    except Exception as e:
        print(f"Error al calcular cantidad adicional: {e}")
        return 0.0

def actualizar_cantidad_adicional_en_factura(factura_id: int):
    nueva_cantidad = calcular_cantidad_adicional(factura_id)
    try:
        with get_cursor() as cursor:
            sql = "UPDATE facturas SET cantidad_adicional = %s WHERE numero_factura = %s"
            cursor.execute(sql, (nueva_cantidad, factura_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad adicional: {e}")
        return False


