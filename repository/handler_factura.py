import pymysql
from models.facturas import FacturaDB
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
            sql = "SELECT * FROM facturas"
            cursor.execute(sql)
            facturas = cursor.fetchall()
            return [FacturaDB(**factura) for factura in facturas]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar facturas: {e}")
        return []

def get_factura_by_id(numero_factura: int):
    try:
        with get_cursor() as cursor:
            # Recupera la factura normal
            sql = "SELECT * FROM facturas WHERE numero_factura = %s"
            cursor.execute(sql, (numero_factura,))
            factura = cursor.fetchone()
            if not factura:
                return None

            # Calcula la cantidad adicional en tiempo real
            sql_sum = """
                SELECT SUM(fp.cantidad * p.precio) AS cantidad_adicional
                FROM factura_producto fp
                JOIN productos p ON fp.producto_id = p.id
                WHERE fp.factura_id = %s
            """
            cursor.execute(sql_sum, (numero_factura,))
            row = cursor.fetchone()
            factura["cantidad_adicional"] = row["cantidad_adicional"] if row and row["cantidad_adicional"] is not None else 0.0

            return FacturaDB(**factura)
    except Exception as e:
        print(f"Error al recuperar factura por id: {e}")
        return None


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
                FROM factura_producto fp
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


