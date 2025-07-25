# -*- coding: utf-8 -*-
# Raspador dinámico para sitios web con contenido JavaScript

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests, hashlib, os, time, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from db.database import obtener_conexion, guardar_archivo
from db.logger import logger
from datetime import datetime

BASE_URL = "http://localhost:5500/"  # Puerto donde corre el frontend Flask
CARPETA_DESCARGAS = "descargas_dinamicas"
TIEMPO_ESPERA = 10  # Segundos para esperar elementos
SCROLL_PAUSA = 2    # Pausa entre scrolls para cargar contenido lazy

# Configuración de Chrome para Selenium
def configurar_driver():
    """Configura y retorna el driver de Chrome para Selenium"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Configurar descargas automáticas
    prefs = {
        "download.default_directory": os.path.abspath(CARPETA_DESCARGAS),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Error configurando Chrome driver: {e}")
        return None

# Generar hash SHA-256 del contenido del archivo
def hash_archivo(contenido):
    """Genera hash SHA-256 del contenido del archivo"""
    return hashlib.sha256(contenido).hexdigest()

# Hacer scroll en la página para cargar contenido lazy
def hacer_scroll_completo(driver):
    """Hace scroll completo en la página para cargar todo el contenido dinámico"""
    logger.info("Realizando scroll para cargar contenido dinámico...")
    
    # Obtener altura inicial
    altura_anterior = 0
    altura_actual = driver.execute_script("return document.body.scrollHeight")
    
    while altura_anterior != altura_actual:
        altura_anterior = altura_actual
        
        # Hacer scroll hacia abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSA)
        
        # Obtener nueva altura
        altura_actual = driver.execute_script("return document.body.scrollHeight")
        logger.debug(f"Altura de página: {altura_actual}")
    
    # Volver al inicio
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

# Esperar a que carguen elementos específicos
def esperar_elementos_dinamicos(driver):
    """Espera a que carguen elementos dinámicos comunes"""
    try:
        # Esperar por elementos comunes que indican carga completa
        wait = WebDriverWait(driver, TIEMPO_ESPERA)
        
        # Intentar esperar por diferentes tipos de elementos
        selectores = [
            "a[href*='.pdf']",
            "a[href*='.jpg']", 
            "a[href*='.png']",
            "a[href*='.docx']",
            "[data-loaded='true']",
            ".loaded",
            ".content-ready"
        ]
        
        for selector in selectores:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.debug(f"Elementos encontrados con selector: {selector}")
                break
            except TimeoutException:
                continue
                
    except Exception as e:
        logger.warning(f"Timeout esperando elementos dinámicos: {e}")

# Extraer archivos de JavaScript/AJAX responses
def extraer_archivos_ajax(driver):
    """Extrae URLs de archivos desde respuestas AJAX o APIs"""
    archivos_ajax = []
    
    try:
        # Ejecutar JavaScript para obtener datos de APIs
        scripts_busqueda = [
            # Buscar en window object
            "return window.filesList || window.files || window.documents || [];",
            # Buscar en localStorage
            "return JSON.parse(localStorage.getItem('files') || '[]');",
            # Buscar en sessionStorage  
            "return JSON.parse(sessionStorage.getItem('files') || '[]');",
            # Buscar variables globales comunes
            "return window.data?.files || window.appData?.files || [];"
        ]
        
        for script in scripts_busqueda:
            try:
                resultado = driver.execute_script(script)
                if resultado and isinstance(resultado, list):
                    archivos_ajax.extend(resultado)
                    logger.info(f"Encontrados {len(resultado)} archivos via JavaScript")
            except Exception as e:
                logger.debug(f"Script fallido: {script[:50]}... Error: {e}")
                
    except Exception as e:
        logger.warning(f"Error extrayendo archivos AJAX: {e}")
    
    return archivos_ajax

# Función principal para raspar sitio dinámico
def raspar_sitio_dinamico():
    """Función principal para realizar scraping dinámico"""
    
    # Crear carpeta de descargas
    if not os.path.exists(CARPETA_DESCARGAS):
        os.makedirs(CARPETA_DESCARGAS)
    
    # Crear tabla de base de datos
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS archivos_dinamicos (
                id SERIAL PRIMARY KEY,
                nombre_archivo TEXT,
                url TEXT,
                sha256 TEXT,
                metodo_extraccion TEXT,
                fecha_descarga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_vista TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.exception("Error creando tabla archivos_dinamicos")
        return
    
    # Configurar driver
    driver = configurar_driver()
    if not driver:
        logger.error("No se pudo configurar el driver de Chrome")
        return
    
    archivos_encontrados = {}
    
    try:
        logger.info("Iniciando raspado dinámico...")
        
        # Cargar página principal
        driver.get(BASE_URL)
        logger.info(f"Página cargada: {BASE_URL}")
        
        # Esperar elementos dinámicos
        esperar_elementos_dinamicos(driver)
        
        # Hacer scroll completo
        hacer_scroll_completo(driver)
        
        # Esperar un poco más para asegurar carga completa
        time.sleep(3)
        
        # Obtener HTML renderizado
        html_renderizado = driver.page_source
        soup = BeautifulSoup(html_renderizado, "html.parser")
        
        # 1. Extraer enlaces estáticos del HTML renderizado
        logger.info("Extrayendo enlaces del HTML renderizado...")
        enlaces = soup.find_all("a", href=True)
        
        for enlace in enlaces:
            href = enlace["href"]
            if any(href.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx", ".zip", ".xlsx"]):
                url_completa = urljoin(BASE_URL, href)
                nombre_archivo = os.path.basename(urlparse(url_completa).path)
                
                if nombre_archivo:  # Asegurar que tenga nombre
                    archivos_encontrados[nombre_archivo] = {
                        'url': url_completa,
                        'metodo': 'HTML_RENDERIZADO'
                    }
                    logger.debug(f"Archivo encontrado en HTML: {nombre_archivo}")
        
        # 2. Extraer archivos de respuestas AJAX/JavaScript
        logger.info("Extrayendo archivos de JavaScript/AJAX...")
        archivos_ajax = extraer_archivos_ajax(driver)
        
        for archivo_info in archivos_ajax:
            if isinstance(archivo_info, dict) and 'url' in archivo_info:
                url_archivo = archivo_info['url']
                nombre = archivo_info.get('name') or os.path.basename(urlparse(url_archivo).path)
                
                if nombre:
                    archivos_encontrados[nombre] = {
                        'url': url_archivo,
                        'metodo': 'AJAX_JS'
                    }
                    logger.debug(f"Archivo encontrado en AJAX: {nombre}")
        
        # 3. Buscar elementos con atributos data-* que contengan URLs
        logger.info("Buscando elementos con data-attributes...")
        elementos_data = soup.find_all(attrs={"data-file": True})
        elementos_data.extend(soup.find_all(attrs={"data-url": True}))
        elementos_data.extend(soup.find_all(attrs={"data-download": True}))
        
        for elemento in elementos_data:
            for attr in ['data-file', 'data-url', 'data-download']:
                if elemento.get(attr):
                    url_archivo = urljoin(BASE_URL, elemento[attr])
                    nombre = os.path.basename(urlparse(url_archivo).path)
                    
                    if nombre and any(nombre.lower().endswith(ext) for ext in [".pdf", ".jpg", ".png", ".docx", ".zip", ".xlsx"]):
                        archivos_encontrados[nombre] = {
                            'url': url_archivo,
                            'metodo': 'DATA_ATTRIBUTES'
                        }
                        logger.debug(f"Archivo encontrado en data-attr: {nombre}")
        
        # 4. Procesar todos los archivos encontrados
        logger.info(f"Procesando {len(archivos_encontrados)} archivos encontrados...")
        
        for nombre_archivo, info_archivo in archivos_encontrados.items():
            try:
                url_archivo = info_archivo['url']
                metodo = info_archivo['metodo']
                ruta_local = os.path.join(CARPETA_DESCARGAS, nombre_archivo)
                
                # Descargar archivo
                response = requests.get(url_archivo, timeout=30)
                response.raise_for_status()
                
                contenido = response.content
                sha256 = hash_archivo(contenido)
                
                # Verificar en base de datos
                conn = obtener_conexion()
                cur = conn.cursor()
                cur.execute("SELECT sha256 FROM archivos_dinamicos WHERE nombre_archivo = %s;", (nombre_archivo,))
                resultado = cur.fetchone()
                
                if resultado is None:
                    # Archivo nuevo
                    with open(ruta_local, "wb") as f:
                        f.write(contenido)
                    
                    cur.execute(
                        "INSERT INTO archivos_dinamicos (nombre_archivo, url, sha256, metodo_extraccion) VALUES (%s, %s, %s, %s);",
                        (nombre_archivo, url_archivo, sha256, metodo)
                    )
                    logger.info(f"[NUEVO][{metodo}] {nombre_archivo} descargado")
                    
                elif resultado[0] != sha256:
                    # Archivo modificado
                    with open(ruta_local, "wb") as f:
                        f.write(contenido)
                    
                    cur.execute(
                        "UPDATE archivos_dinamicos SET sha256 = %s, ultima_vista = CURRENT_TIMESTAMP WHERE nombre_archivo = %s;",
                        (sha256, nombre_archivo)
                    )
                    logger.warning(f"[CAMBIADO][{metodo}] {nombre_archivo} actualizado")
                    
                else:
                    # Archivo sin cambios
                    cur.execute(
                        "UPDATE archivos_dinamicos SET ultima_vista = CURRENT_TIMESTAMP WHERE nombre_archivo = %s;",
                        (nombre_archivo,)
                    )
                    logger.debug(f"[SIN_CAMBIOS][{metodo}] {nombre_archivo}")
                
                conn.commit()
                cur.close()
                conn.close()
                
            except Exception as e:
                logger.error(f"Error procesando {nombre_archivo}: {e}")
        
        # 5. Limpiar archivos eliminados
        try:
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT nombre_archivo FROM archivos_dinamicos;")
            archivos_bd = [fila[0] for fila in cur.fetchall()]
            
            for archivo_bd in archivos_bd:
                if archivo_bd not in archivos_encontrados:
                    logger.warning(f"[ELIMINADO] {archivo_bd} ya no está disponible")
                    try:
                        os.remove(os.path.join(CARPETA_DESCARGAS, archivo_bd))
                    except:
                        pass
                    cur.execute("DELETE FROM archivos_dinamicos WHERE nombre_archivo = %s;", (archivo_bd,))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.exception("Error en limpieza de archivos")
        
    except Exception as e:
        logger.exception("Error durante raspado dinámico")
        
    finally:
        # Cerrar driver
        if driver:
            driver.quit()
            logger.info("Driver de Chrome cerrado")
    
    logger.info("Raspado dinámico completado")

# Función para raspar sitio específico con SPA (Single Page Application)
def raspar_spa(url_base, selectores_personalizados=None):
    """Función especializada para aplicaciones SPA"""
    
    driver = configurar_driver()
    if not driver:
        return
    
    try:
        logger.info(f"Raspando SPA: {url_base}")
        driver.get(url_base)
        
        # Esperar por selector personalizado si se proporciona
        if selectores_personalizados:
            wait = WebDriverWait(driver, TIEMPO_ESPERA)
            for selector in selectores_personalizados:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"Elemento SPA cargado: {selector}")
                    break
                except TimeoutException:
                    continue
        
        # Simular interacciones del usuario para activar carga de contenido
        try:
            # Hacer clic en pestañas o botones que puedan cargar contenido
            botones = driver.find_elements(By.CSS_SELECTOR, "button, .tab, .nav-item")
            for boton in botones[:5]:  # Limitar a 5 para evitar bucles infinitos
                try:
                    driver.execute_script("arguments[0].click();", boton)
                    time.sleep(2)  # Esperar carga
                except:
                    continue
        except Exception as e:
            logger.debug(f"Error en simulación de clicks: {e}")
        
        # Continuar con extracción normal
        hacer_scroll_completo(driver)
        return driver.page_source
        
    except Exception as e:
        logger.error(f"Error raspando SPA: {e}")
        return None
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    raspar_sitio_dinamico()