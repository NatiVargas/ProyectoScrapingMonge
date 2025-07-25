# -*- coding: utf-8 -*-
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from db.logger import logger
from db.database import guardar_producto
import json
from datetime import datetime
from scraper.static_scraper import scrapear_sitio_estatico
from llm import llm_selector

# Clase principal para el scraping de Tienda Monge
class ScraperTiendaMonge:
    def __init__(self):
        self.logger = logger

    def hacer_scroll(self, driver):
        """Realiza scroll hasta el final de la página."""
        altura_final = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            nueva_altura = driver.execute_script("return document.body.scrollHeight")
            if nueva_altura == altura_final:
                break
            altura_final = nueva_altura

    def siguiente_pagina(self, driver):
        """Hace clic en el botón de siguiente página si existe."""
        try:
            boton_siguiente = driver.find_element(By.CSS_SELECTOR, "li.ais-Pagination-item--nextPage a")
            url_siguiente = boton_siguiente.get_attribute("href")
            if url_siguiente:
                driver.get(url_siguiente)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                return True
            return False
        except Exception:
            return False

    def extraer_productos(self, driver):
        """Extrae los productos de la página actual."""
        productos = []

        # Estructura Magento
        magento_items = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
        for item in magento_items:
            try:
                titulo = item.find_element(By.CSS_SELECTOR, ".product-item-name a").text.strip()
                precio = item.find_element(By.CSS_SELECTOR, ".special-price .price").text.strip()
                imagen = item.find_element(By.CSS_SELECTOR, "img.product-image-photo").get_attribute("src")
                url = item.find_element(By.CSS_SELECTOR, "a.product-item-link").get_attribute("href")
                productos.append({"titulo": titulo, "precio": precio, "imagen_url": imagen, "url": url})
            except Exception as e:
                self.logger.warning(f"[MAGENTO] Producto con error: {e}")

        # Estructura SPA (Algolia)
        spa_items = driver.find_elements(By.CSS_SELECTOR, "li.ais-Hits-item")
        for item in spa_items:
            try:
                titulo = item.find_element(By.CSS_SELECTOR, "h3.result-title").text.strip()
                precio = item.find_element(By.CSS_SELECTOR, ".after_special").text.strip()
                imagen = item.find_element(By.CSS_SELECTOR, ".result-thumbnail img").get_attribute("src")
                url = item.find_element(By.CSS_SELECTOR, "a.result").get_attribute("href")
                productos.append({"titulo": titulo, "precio": precio, "imagen_url": imagen, "url": url})
            except Exception as e:
                self.logger.warning(f"[SPA] Producto con error: {e}")

        return productos

    def scrapear_sitio_web(self):
        """Inicia el scraping en el sitio web de Tienda Monge."""
        self.logger.info("Iniciando scraping en Tienda Importadora Monge...")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.tiendamonge.com/productos/celulares-y-tablets/celulares")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        while True:
            self.hacer_scroll(driver)
            productos_en_pagina = self.extraer_productos(driver)
            for producto in productos_en_pagina:
                guardar_producto(producto["titulo"], producto["precio"], producto["imagen_url"])
            if not self.siguiente_pagina(driver):
                break

        driver.quit()
        self.logger.info("Scraping finalizado.")

    def ejecutar_scraping_completo(self):
        """Ejecuta todo el proceso de scraping y generación de archivos."""
        self.logger.info("=== INICIO: Ejecución completa del sistema ===")
        try:
            # 1. Scraping real con Selenium
            self.logger.info("Iniciando scraping con Selenium desde Tienda Monge...")
            self.scrapear_sitio_web()
            self.logger.info("Scraping con Selenium completado.")

            # 2. Scraping de archivos locales (si aplica)
            self.logger.info("Iniciando scraping de archivos estáticos (localhost)...")
            scrapear_sitio_estatico()
            self.logger.info("Scraping de archivos estáticos completado.")

            # 3. Generar archivos JSON para el dashboard web
            self.logger.info("Generando results.json desde la base de datos...")
            exportar_productos_a_json()

            self.logger.info("Generando files.json desde la base de datos...")
            exportar_archivos_a_json()

            # 4. Probar selector con LLM (opcional / demo)
            self.logger.info("Probando generación de selector LLM (OpenAI)...")
            fragmento_html = """
            <div class='product-card'>
                <div class='product-title'>iPhone 13</div>
                <div class='product-price'>₡850000</div>
            </div>
            """
            selector_css = llm_selector.generar_selector(fragmento_html, "product price", modo="css")
            print(f"Selector sugerido (CSS): {selector_css}")


            self.logger.info("=== FIN: Ejecución completa del sistema ===")

        except Exception as e:
            self.logger.error("Ocurrió un error crítico durante la ejecución.")
            traceback.print_exc()


# Función para exportar productos a JSON
def exportar_productos_a_json(ruta_salida="data/results.json"):
    try:
        from db.database import obtener_conexion
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT titulo, precio FROM productos ORDER BY id DESC;")
        filas = cur.fetchall()
        cur.close()
        conn.close()
        resultados = []
        for i, fila in enumerate(filas):
            resultados.append({
                "id": i + 1,
                "title": fila[0],
                "category": "Celulares",
                "description": f"Precio: {fila[1]}",
                "date": datetime.now().isoformat()
            })
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"Archivo '{ruta_salida}' generado correctamente con {len(resultados)} productos.")
    except Exception as e:
        print("Error al generar results.json:", e)

# Función para exportar archivos a JSON
def exportar_archivos_a_json(ruta_salida="data/files.json"):
    try:
        from db.database import obtener_conexion
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT filename, url FROM downloaded_files ORDER BY id DESC;")
        filas = cur.fetchall()
        cur.close()
        conn.close()
        archivos = []
        for i, fila in enumerate(filas):
            nombre_archivo = fila[0]
            url = fila[1]
            ext = nombre_archivo.split('.')[-1].lower()
            tamano = 1024000  # Puedes calcularlo si los archivos son locales, o dejar un valor fijo
            archivos.append({
                "id": i + 1,
                "nombre_archivo": nombre_archivo,
                "tipo": ext.upper(),
                "tamano": tamano,
                "url": url
            })
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(archivos, f, indent=2, ensure_ascii=False)
        print(f"Archivo '{ruta_salida}' generado correctamente con {len(archivos)} archivos.")
    except Exception as e:
        print("Error al generar files.json:", e)

if __name__ == "__main__":
    print("Lanzando: Reto Técnico Completo VoiceFlip...")
    scraper = ScraperTiendaMonge()
    scraper.ejecutar_scraping_completo()
    input("Presiona cualquier tecla para salir...")