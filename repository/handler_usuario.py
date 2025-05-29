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
                (nombre, apellido1, apellido2, email, contraseña, telefono, fecha_nacimiento, especialidad,
                 numero_seguridad_social, admin_empresa, empresa_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                usuario["nombre"],
                usuario["apellido1"],
                usuario.get("apellido2"),
                usuario["email"],
                usuario["contraseña"],
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

def verificar_credenciales(email, contraseña):
    """
    Verifica si existe un usuario con ese email y contraseña.
    """
    try:
        with get_cursor() as cursor:
            sql = "SELECT contraseña FROM usuarios WHERE email = %s"
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()
            if usuario is None:
                print("Usuario no encontrado.")
                return False
            if usuario["contraseña"] == contraseña:
                return True
            else:
                print("Contraseña incorrecta.")
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

def eliminar_usuario(usuario_id: int):
    try:
        with get_cursor() as cursor:
            sql = "DELETE FROM usuarios WHERE id = %s"
            cursor.execute(sql, (usuario_id,))
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al eliminar usuario: {e}")
        return False

def get_usuarios_by_empresa(empresa_id: str):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM usuarios WHERE empresa_id = %s"
            cursor.execute(sql, (empresa_id,))
            usuarios = cursor.fetchall()
            return [UsuarioDB(**usuario) for usuario in usuarios]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar usuarios por empresa: {e}")
        return []

def get_usuario_by_email(email: str):
    try:
        with get_cursor() as cursor:
            sql = "SELECT * FROM usuarios WHERE email = %s"
            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()
            return UsuarioDB(**usuario) if usuario else None
    except pymysql.MySQLError as e:
        print(f"Error al recuperar usuario por email: {e}")
        return None

def get_usuarios_ordenados_por_columna(columna: str = "nombre", ascendente: bool = True, skip: int = 0, limit: int = 100):
    # Definir el mapeo de nombres "visibles" a nombres reales en la base de datos
    columnas_validas = {
        "usuario": "email",
        "nombre": "nombre",
        "apellidos": "apellido1",  # Si quieres, también puedes concatenar apellido1 y apellido2
        "rol": "admin_empresa",    # Cambia si tienes un campo 'rol' real
        "activo": "activo",
        "int_ext": "interno_externo"  # Cambia si el campo se llama diferente
    }
    # Si la columna no es válida, usar por defecto "nombre"
    columna_bd = columnas_validas.get(columna, "nombre")
    orden = "ASC" if ascendente else "DESC"

    try:
        with get_cursor() as cursor:
            sql = f"SELECT * FROM usuarios ORDER BY {columna_bd} {orden} LIMIT %s OFFSET %s"
            cursor.execute(sql, (limit, skip))
            usuarios = cursor.fetchall()
            return [UsuarioDB(**usuario) for usuario in usuarios]
    except pymysql.MySQLError as e:
        print(f"Error al recuperar usuarios: {e}")
        return []


def actualizar_usuario(usuario_id: int, campos: dict):
    if not campos:
        return False  # Nada que actualizar

    try:
        with get_cursor() as cursor:
            set_clause = ", ".join(f"{k} = %s" for k in campos)
            valores = list(campos.values())
            valores.append(usuario_id)
            sql = f"UPDATE usuarios SET {set_clause} WHERE id = %s"
            cursor.execute(sql, valores)
            return cursor.rowcount > 0
    except pymysql.MySQLError as e:
        print(f"Error al actualizar usuario: {e}")
        return False

def contar_incidencias_en_curso(cliente_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT COUNT(*) AS total
                FROM incidencias
                WHERE cliente_id = %s AND estado = 'En Curso'
            """
            cursor.execute(sql, (cliente_id,))
            row = cursor.fetchone()
            return row["total"] if row else 0
    except pymysql.MySQLError as e:
        print(f"Error al contar incidencias en curso: {e}")
        return 0

def contar_incidencias_totales(cliente_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT COUNT(*) AS total
                FROM incidencias
                WHERE cliente_id = %s
            """
            cursor.execute(sql, (cliente_id,))
            row = cursor.fetchone()
            return row["total"] if row else 0
    except pymysql.MySQLError as e:
        print(f"Error al contar incidencias totales: {e}")
        return 0

def get_clientes_by_empresa_id(empresa_id: str):
    try:
        with get_cursor() as cursor:
            sql = """
            SELECT id, nombre, apellido1, apellido2, email, telefono
            FROM usuarios
            WHERE
            (numero_seguridad_social IS NULL OR numero_seguridad_social = '')
            AND (especialidad IS NULL OR especialidad = '')
            AND (admin_empresa IS NULL OR admin_empresa = 0)
            AND empresa_id = %s;
                """
            cursor.execute(sql, (empresa_id,))
            clientes = cursor.fetchall()
            return clientes
    except Exception as e:
        print(f"Error al obtener clientes por empresa: {e}")
        return []

def get_cliente_by_id(cliente_id: int):
    try:
        with get_cursor() as cursor:
            sql = """
                SELECT id, nombre, apellido1, apellido2, email, telefono
                FROM usuarios
                WHERE id = %s
                LIMIT 1;
            """
            cursor.execute(sql, (cliente_id,))
            cliente = cursor.fetchone()
            if cliente:
                return cliente
            else:
                return None
    except Exception as e:
        print(f"Error al obtener detalle de cliente: {e}")
        return None



