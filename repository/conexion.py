import os
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager

# Carga la configuración desde variables de entorno (o usa estos valores por defecto)
DB_HOST     = os.getenv('DB_HOST', 'localhost')
DB_PORT     = int(os.getenv('DB_PORT', 3306))
DB_USER     = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Nomevale4')
DB_NAME     = os.getenv('DB_NAME', 'ServiTech')
DB_CHARSET  = 'utf8mb4'

@contextmanager
def get_connection():
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset=DB_CHARSET,
        cursorclass=DictCursor,
        autocommit=False
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def get_cursor():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            yield cursor

