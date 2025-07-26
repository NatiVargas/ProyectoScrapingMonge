# llm/llm_selector.py
import os
from pathlib import Path
from dotenv import load_dotenv
from mistralai import Mistral

# Cargar el .env desde la raíz del proyecto
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

if not API_KEY:
    raise ValueError("MISTRAL_API_KEY no está definida en el archivo .env")

# Crear cliente Mistral
client = Mistral(api_key=API_KEY)

def generar_selector(fragmento_html: str, objetivo: str, modo: str = "css") -> str:
    """
    Utiliza Mistral para sugerir un selector CSS o XPath.
    :param fragmento_html: Fragmento HTML que contiene el objetivo.
    :param objetivo: Descripción del contenido a extraer.
    :param modo: "css" o "xpath".
    :return: Selector sugerido (string).
    """
    prompt = (
        f"Eres un experto en scraping web. Dado el siguiente fragmento HTML, "
        f"proporciona únicamente un selector válido {modo.upper()} para extraer el '{objetivo}'. "
        f"No agregues explicaciones, devuelve solo el selector.\n\n{fragmento_html}"
    )

    try:
        resp = client.chat.complete(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en HTML, scraping web y automatización. Responde solo con el selector limpio."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=100,
        )

        # La librería retorna el texto en:
        # resp.choices[0].message.content   (SDK mistralai >= 0.1.0)
        return resp.choices[0].message.content.strip()

    except Exception as e:
        # Loguea / propaga el error según te convenga
        raise RuntimeError(f"Error llamando a Mistral: {e}") from e


# Prueba rápida directa (si ejecutas este módulo solo)
if __name__ == "__main__":
    html = """
    <div class='product-card'>
        <div class='product-title'>Laptop Gamer</div>
        <div class='product-price'>₡350000</div>
    </div>
    """
    print(generar_selector(html, "precio del producto", modo="css"))
