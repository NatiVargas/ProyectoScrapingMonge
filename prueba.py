from llm.llm_selector import generar_selector

html = """
<div class="producto">
    <span class="nombre">Laptop Lenovo</span>
    <span class="precio">₡299.900</span>
</div>
"""

selector = generar_selector(html, "precio del producto", modo="css")
print("Selector sugerido:", selector)
