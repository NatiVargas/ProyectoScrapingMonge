# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
from main import ScraperTiendaMonge, exportar_productos_a_json, exportar_archivos_a_json

def ejecutar_scraping_y_actualizar_json():
    """Ejecuta el scraping básico y actualiza los archivos JSON"""
    print("Iniciando scraping programado...")
    scraper = ScraperTiendaMonge()
    scraper.scrapear_sitio_web()  # Solo scraping del sitio web principal
    exportar_productos_a_json()
    exportar_archivos_a_json()
    print("Scraping y exportación completados.")

def ejecutar_proceso_completo():
    """Ejecuta todo el flujo completo de scraping"""
    print("Iniciando proceso completo de scraping...")
    scraper = ScraperTiendaMonge()
    scraper.ejecutar_scraping_completo()  # Todo el proceso (web + estático + LLM)
    print("Proceso completo de scraping finalizado.")

# Configuración del programador de tareas
programador = BlockingScheduler()
programador.add_job(ejecutar_scraping_y_actualizar_json, 'interval', hours=1)  # Cada hora
programador.add_job(ejecutar_proceso_completo, 'interval', hours=6)  # Cada 6 horas

# Iniciar el programador
if __name__ == "__main__":
    print("Programador iniciado. Ejecutando tareas programadas...")
    ejecutar_scraping_y_actualizar_json()  # Ejecutar inmediatamente al iniciar
    programador.start()