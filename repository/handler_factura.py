import pymysql
from models.factura import FacturaDB
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
            sql = "SELECT * FROM facturas WHERE numero_factura = %s"
            cursor.execute(sql, (numero_factura,))
            factura = cursor.fetchone()
            return FacturaDB(**factura) if factura else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar factura por id: {e}")
        return None
