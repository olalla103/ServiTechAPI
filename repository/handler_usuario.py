import pymysql

from models.usuarios import UsuarioDB
from repository.conexion import get_cursor

def insertar_usuario(usuario):
    """
    usuario: dict con las claves según la estructura de la tabla usuarios
    """
    try:
        with get_cursor() as cursor:
            sql = """
                INSERT INTO usuarios 
                (nombre, apellido1, apellido2, telefono, fecha_nacimiento, especialidad,
                 numero_seguridad_social, admin_empresa, empresa_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                usuario["nombre"],
                usuario["apellido1"],
                usuario.get("apellido2"),
                usuario.get("telefono"),
                usuario.get("fecha_nacimiento"),
                usuario.get("especialidad"),
                usuario.get("numero_seguridad_social"),
                usuario.get("admin_empresa", 0),  # 0 por defecto
                usuario.get("empresa_id")
            )
            cursor.execute(sql, valores)
            return cursor.lastrowid
    except pymysql.MySQLError as e:
        print(f"Error al insertar usuario: {e}")
        return None

def get_all_usuarios():
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM usuarios"
            cursor.execute(sql)
            usuarios = cursor.fetchall()
            return [UsuarioDB(**usuario) for usuario in usuarios]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar usuarios: {e}")
        return []

def get_usuario_by_id(usuario_id: int):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM usuarios WHERE id = %s"
            cursor.execute(sql, (usuario_id,))
            usuario = cursor.fetchone()
            return UsuarioDB(**usuario) if usuario else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar usuario por id: {e}")
        return None

def get_usuario_by_nombre_apellidos(nombre: str, apellido1: str, apellido2: str):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT * FROM usuarios
                WHERE nombre = %s AND apellido1 = %s AND apellido2 = %s
            """
            cursor.execute(sql, (nombre, apellido1, apellido2))
            usuario = cursor.fetchone()
            return UsuarioDB(**usuario) if usuario else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar usuario por nombre y apellidos: {e}")
        return None

def verificar_credenciales(id_usuario, numero_seguridad_social):
    """
    Verifica si el usuario con ese id tiene el número de seguridad social dado.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT numero_seguridad_social FROM usuarios WHERE id = %s"
            cursor.execute(sql, (id_usuario,))
            usuario = cursor.fetchone()
            if usuario is None:
                print("Usuario no encontrado.")
                return False
            if usuario["numero_seguridad_social"] == numero_seguridad_social:
                return True
            else:
                print("Número de seguridad social incorrecto.")
                return False
    except pymysql.MySQLError as e:
        print(f"Error al verificar credenciales: {e}")
        return False

def cambiar_telefono(id_usuario, nuevo_telefono):
    """
    Cambia el teléfono del usuario indicado por id.
    """
    try:
        with get_cursor() as cursor:
            sql = "UPDATE usuarios SET telefono = %s WHERE id = %s"
            cursor.execute(sql, (nuevo_telefono, id_usuario))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al cambiar el teléfono: {e}")
        return False

def recuperar_emails():
    """
    Recupera todos los emails de los usuarios.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT email FROM usuarios"
            cursor.execute(sql)
            emails = [row["email"] for row in cursor.fetchall()]
            return emails
    except pymysql.MySQLError as e:
        print(f"Error al recuperar emails: {e}")
        return []

def recuperar_telefonos():
    """
    Recupera todos los teléfonos de los usuarios.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT telefono FROM usuarios"
            cursor.execute(sql)
            telefonos = [row["telefono"] for row in cursor.fetchall()]
            return telefonos
    except pymysql.MySQLError as e:
        print(f"Error al recuperar teléfonos: {e}")
        return []

def recuperar_especialidad(id_usuario):
    """
    Recupera la especialidad del usuario dado su id.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT especialidad FROM usuarios WHERE id = %s"
            cursor.execute(sql, (id_usuario,))
            usuario = cursor.fetchone()
            if usuario is None:
                print("Usuario no encontrado.")
                return None
            else:
                return usuario["especialidad"]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar especialidad: {e}")
        return None
