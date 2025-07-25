
# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si es necesario
load_dotenv()

# Configuración del cliente OpenAI para Azure
ENDPOINT = "https://voiceflip-openai.openai.azure.com/"
DEPLOYMENT_ID = "gpt-4o"  
API_KEY = "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"
API_VERSION = "2025-01-01-preview"

client = OpenAI(
    api_key=API_KEY,
    base_url=f"{ENDPOINT}/openai/deployments/{DEPLOYMENT_ID}",
    default_headers={"api-key": API_KEY},
)

# Función para generar un selector CSS o XPath usando un modelo LLM
def generar_selector(fragmento_html: str, objetivo: str, modo: str = "css") -> str:
    """
    Utiliza un modelo LLM para sugerir un selector CSS o XPath.
    :param fragmento_html: Fragmento HTML que contiene el objetivo
    :param objetivo: Descripción del contenido a extraer
    :param modo: "css" o "xpath"
    :return: Selector sugerido
    """
    prompt = (
        f"Eres un experto en scraping web. Dado el siguiente fragmento HTML, "
        f"proporciona un selector válido {modo.upper()} para extraer el '{objetivo}':\n\n{fragmento_html}"
    )
    respuesta = client.chat.completions.create(
        model=DEPLOYMENT_ID,
        messages=[
            {"role": "system", "content": "Eres un experto en HTML, scraping web y automatización. Responde solo con el selector limpio."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        top_p=1.0,
        max_tokens=100
    )
    return respuesta.choices[0].message.content.strip()

# Ejemplo de uso
if __name__ == "__main__":
    html_ejemplo = """
    <div class='product-card'>
        <div class='product-title'>Laptop Gamer</div>
        <div class='product-price'>₡350000</div>
    </div>
    """
    objetivo = "precio del producto"
    tipo_selector = "css"  # o "xpath"
    # Generar el selector usando el modelo
    selector = generar_selector(html_ejemplo, objetivo, tipo_selector)
    print(f"Selector sugerido ({tipo_selector}): {selector}")