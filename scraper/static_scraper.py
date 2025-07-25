
# -*- coding: utf-8 -*-
# Scraper para un sitio web estático local
import requests, hashlib, os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from db.database import obtener_conexion
from db.logger import logger
from datetime import datetime
# Configuración de localhost para la web
#BASE_URL = "http://localhost:8000/"
BASE_URL = "http://localhost:5500/"
CARPETA_DESCARGAS = "downloads"
# Genera el hash SHA-256 del contenido de un archivo
def hash_archivo(contenido):
    return hashlib.sha256(contenido).hexdigest()
# Función principal para scrapear un sitio estático
def scrapear_sitio_estatico():
    if not os.path.exists(CARPETA_DESCARGAS):
        os.makedirs(CARPETA_DESCARGAS)
    # Crear la tabla en la base de datos si no existe
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                url TEXT,
                sha256 TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.exception("No se pudo crear la tabla downloaded_files")
    # Log del inicio del scraping
    logger.info("Iniciando scraping desde el sitio local")
    respuesta = requests.get(BASE_URL)
    sopa = BeautifulSoup(respuesta.content, "html.parser")
    # Diccionario para almacenar archivos encontrados y sus hashes
    archivos_encontrados = {}
    # Scraping de enlaces HTML estáticos
    try:
        logger.info("Iniciando scraping HTML desde el sitio local")
        respuesta = requests.get(BASE_URL)
        sopa = BeautifulSoup(respuesta.content, "html.parser")
        archivos = sopa.find_all("a", href=True)
        # Filtrar enlaces para encontrar archivos con extensiones específicas
        for enlace_archivo in archivos:
            href = enlace_archivo["href"]
            if any(href.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx"]):
                url_completa = urljoin(BASE_URL, href)
                nombre_archivo = os.path.basename(href)
                ruta_local = os.path.join(CARPETA_DESCARGAS, nombre_archivo)
                # Verificar si el archivo ya fue procesado
                respuesta_archivo = requests.get(url_completa)
                contenido = respuesta_archivo.content
                sha256 = hash_archivo(contenido)
                archivos_encontrados[nombre_archivo] = sha256
                # Verificar si el archivo existe en la base de datos
                conn = obtener_conexion()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM downloaded_files WHERE filename = %s;", (nombre_archivo,))
                resultado = cur.fetchone()
                # Si el archivo es nuevo o cambió, guardarlo
                if resultado is None:
                    with open(ruta_local, "wb") as f:
                        f.write(contenido)
                    cur.execute(
                        "INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);",
                        (nombre_archivo, url_completa, sha256)
                    )
                    logger.info(f"[NUEVO][HTML] {nombre_archivo} descargado")
                elif resultado[0] != sha256:
                    with open(ruta_local, "wb") as f:
                        f.write(contenido)
                    cur.execute(
                        "UPDATE downloaded_files SET sha256 = %s, last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (sha256, nombre_archivo)
                    )
                    logger.warning(f"[CAMBIO][HTML] {nombre_archivo} actualizado (hash diferente)")
                else:
                    cur.execute(
                        "UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (nombre_archivo,)
                    )
                # Guardar cambios en la base de datos
                conn.commit()
                cur.close()
                conn.close()
    except Exception as e:
        logger.exception("Error procesando archivos desde HTML")
    # Scraping desde el endpoint de datos JSON
    try:
        logger.info("Obteniendo archivos desde la API JSON...")
        url_json = urljoin(BASE_URL, "data/files.json")
        respuesta = requests.get(url_json)
        if respuesta.status_code == 200:
            datos_archivos = respuesta.json()
            for archivo in datos_archivos:
                url_archivo = archivo.get("url")
                nombre_archivo = os.path.basename(url_archivo)
                ruta_local = os.path.join(CARPETA_DESCARGAS, nombre_archivo)
                # Verificar si el archivo ya fue procesado
                respuesta_archivo = requests.get(url_archivo)
                contenido = respuesta_archivo.content
                sha256 = hash_archivo(contenido)
                archivos_encontrados[nombre_archivo] = sha256
                # Verificar si el archivo existe en la base de datos
                conn = obtener_conexion()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM downloaded_files WHERE filename = %s;", (nombre_archivo,))
                resultado = cur.fetchone()
                # Si el archivo es nuevo o cambió, guardarlo
                if resultado is None:
                    with open(ruta_local, "wb") as f:
                        f.write(contenido)
                    cur.execute(
                        "INSERT INTO downloaded_files (filename, url, sha256) VALUES (%s, %s, %s);",
                        (nombre_archivo, url_archivo, sha256)
                    )
                    logger.info(f"[NUEVO][JSON] {nombre_archivo} descargado desde JSON")
                elif resultado[0] != sha256:
                    with open(ruta_local, "wb") as f:
                        f.write(contenido)
                    cur.execute(
                        "UPDATE downloaded_files SET sha256 = %s, last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (sha256, nombre_archivo)
                    )
                    logger.warning(f"[CAMBIO][JSON] {nombre_archivo} actualizado (hash diferente)")
                else:
                    cur.execute(
                        "UPDATE downloaded_files SET last_seen = CURRENT_TIMESTAMP WHERE filename = %s;",
                        (nombre_archivo,)
                    )
                # Guardar cambios en la base de datos
                conn.commit()
                cur.close()
                conn.close()
        else:
            logger.error(f"No se pudieron obtener archivos JSON: {respuesta.status_code}")
    except Exception as e:
        logger.exception("Error procesando archivos desde JSON")
    # Limpiar archivos que ya no están presentes
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT filename FROM downloaded_files;")
        todos_archivos_db = [row[0] for row in cur.fetchall()]
        # Verificar archivos que ya no se encuentran
        for archivo_db in todos_archivos_db:
            if archivo_db not in archivos_encontrados:
                logger.warning(f"[ELIMINADO] {archivo_db} ya no se encuentra")
                try:
                    os.remove(os.path.join(CARPETA_DESCARGAS, archivo_db))
                except:
                    pass
                cur.execute("DELETE FROM downloaded_files WHERE filename = %s;", (archivo_db,))
        # Finalizar conexión a la base de datos
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.exception("Error durante la verificación de eliminación")
    # Log del fin del scraping
    logger.info("Scraping finalizado.")