import pymysql
from models.producto import ProductoDB
from repository.conexion import get_cursor

def insertar_producto(producto):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO productos (nombre, descripcion_tecnica)
                VALUES (%s, %s)
            """
            valores = (
                producto["nombre"],
                producto["descripcion_tecnica"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar producto: {e}")
        return None

def get_all_productos():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM productos"
            cursor.execute(sql)
            productos = cursor.fetchall()
            return [ProductoDB(**producto) for producto in productos]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar productos: {e}")
        return []

def get_producto_by_id(id_producto: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM productos WHERE id = %s"
            cursor.execute(sql, (id_producto,))
            producto = cursor.fetchone()
            return ProductoDB(**producto) if producto else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar producto por id: {e}")
        return None
