import pymysql
from models.factura_producto import FacturaProductoDB
from repository.conexion import get_cursor

def insertar_factura_producto(factura_producto):
    """
    Inserta una relación producto-factura con la cantidad usada.
    Devuelve el id insertado o None si hay error.
    """
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO factura_producto (factura_id, producto_id, cantidad)
                VALUES (%s, %s, %s)
            """
            valores = (
                factura_producto["factura_id"],
                factura_producto["producto_id"],
                factura_producto["cantidad"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar factura-producto: {e}")
        return None

def get_factura_producto_by_id(id_relacion):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM factura_producto WHERE id = %s"
            cursor.execute(sql, (id_relacion,))
            row = cursor.fetchone()
            return FacturaProductoDB(**row) if row else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar factura-producto: {e}")
        return None

def get_productos_de_factura(factura_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM factura_producto WHERE factura_id = %s"
            cursor.execute(sql, (factura_id,))
            productos = cursor.fetchall()
            return [FacturaProductoDB(**p) for p in productos]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar productos de la factura: {e}")
        return []

def actualizar_factura_producto(id_relacion: int, cantidad: int):
    if cantidad is None:
        return False
    try:
        with get_cursor() as cursor:
            sql = "UPDATE factura_producto SET cantidad = %s WHERE id = %s"
            cursor.execute(sql, (cantidad, id_relacion))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar cantidad en factura-producto: {e}")
        return False


def eliminar_factura_producto(id_relacion: int):
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM factura_producto WHERE id = %s"
            cursor.execute(sql, (id_relacion,))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar factura-producto: {e}")
        return False
