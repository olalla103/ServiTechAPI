import pymysql
from models.factura_producto import FacturaProductoDB
from repository.conexion import get_cursor

def insertar_factura_producto(factura_producto):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO facturaProducto (factura_id, producto_id)
                VALUES (%s, %s)
            """
            valores = (
                factura_producto["factura_id"],
                factura_producto["producto_id"]
            )
            cursor.execute(sql, valores)
            return True
    except pymysql.MySQLError as e:
        print(f"Error al insertar factura-producto: {e}")
        return False

def get_all_factura_producto():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM facturaProducto"
            cursor.execute(sql)
            relaciones = cursor.fetchall()
            return [FacturaProductoDB(**relacion) for relacion in relaciones]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar factura-producto: {e}")
        return []

def get_factura_producto_by_ids(factura_id: int, producto_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM facturaProducto WHERE factura_id = %s AND producto_id = %s"
            cursor.execute(sql, (factura_id, producto_id))
            relacion = cursor.fetchone()
            return FacturaProductoDB(**relacion) if relacion else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar factura-producto por ids: {e}")
        return None
