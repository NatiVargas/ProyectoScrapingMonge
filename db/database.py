
# -*- coding: utf-8 -*-
# Importaciones y referencias
import psycopg2  # Adaptador para PostgreSQL
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from logger import logger

# Obtener credenciales desde un archivo de texto (más seguro que hardcodear)
def obtener_credenciales():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_credenciales = os.path.join(base_dir, "..", "db_credentials.txt")
        with open(ruta_credenciales, "r") as f:
            lineas = f.read().splitlines()
            return {
                "dbname": lineas[0],
                "user": lineas[1],
                "password": lineas[2],
                "host": lineas[3],
                "port": lineas[4]
            }
    except Exception as e:
        logger.exception("No se pudieron cargar las credenciales del archivo .txt")
        raise

# Conexión a la base de datos
def obtener_conexion():
    credenciales = obtener_credenciales()
    return psycopg2.connect(
        dbname=credenciales["dbname"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

# Guardar productos extraídos del sitio web
def guardar_producto(titulo, precio, url_imagen):
    conn = None
    cursor = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                titulo TEXT,
                precio TEXT,
                url_imagen TEXT
            );
        """)
        cursor.execute(
            "INSERT INTO productos (titulo, precio, url_imagen) VALUES (%s, %s, %s);",
            (titulo, precio, url_imagen)
        )
        conn.commit()
    except Exception as e:
        logger.exception("Error al guardar el producto en la base de datos")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Guardar metadatos de archivos descargados
def guardar_archivo(nombre_archivo, url, sha256):
    conn = None
    cursor = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archivos_descargados (
                id SERIAL PRIMARY KEY,
                nombre_archivo TEXT,
                url TEXT,
                sha256 TEXT,
                fecha_descarga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute(
            "INSERT INTO archivos_descargados (nombre_archivo, url, sha256) VALUES (%s, %s, %s);",
            (nombre_archivo, url, sha256)
        )
        conn.commit()
    except Exception as e:
        logger.exception("Error al guardar la información del archivo en la base de datos")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()