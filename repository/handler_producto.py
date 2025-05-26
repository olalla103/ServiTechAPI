import pymysql
from models.productos import ProductoDB
from repository.conexion import get_cursor

def insertar_producto(producto):
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO productos (nombre, descripcion_tecnica, precio)
                VALUES (%s, %s, %s)
            """
            valores = (
                producto["nombre"],
                producto["descripcion_tecnica"],
                producto["precio"]
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar producto: {e}")
        return None

def actualizar_producto(id_producto: int, campos: dict):
    if not campos:
        return False
    try:
        with get_cursor() as cursor:
            set_clause = ", ".join([f"{k} = %s" for k in campos])
            valores = list(campos.values()) + [id_producto]
            sql = f"UPDATE productos SET {set_clause} WHERE id = %s"
            cursor.execute(sql, valores)
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al actualizar producto: {e}")
        return False

def eliminar_producto(id_producto: int):
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM productos WHERE id = %s"
            cursor.execute(sql, (id_producto,))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar producto: {e}")
        return False

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
