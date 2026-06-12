import requests
from bs4 import BeautifulSoup

url = "https://gamesir.com/es/collections/all-products-1/products/gamesir-x5-lite"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

descripcion = ""
detalles = ""

for bloque in soup.select(".product-accordion.product-info-block"):
    texto = bloque.get_text(" ", strip=True)

    print("\n--- BLOQUE ---")
    print(texto[:500])

    if "Key Features:" in texto:
        descripcion = texto

    if "Compatible Platform:" in texto.replace("\xa0", " "):
        detalles = texto

print("\nDESCRIPCION:")
print(descripcion)

print("\nDETALLES:")
print(detalles)