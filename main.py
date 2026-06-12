from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests

class gamesir_scraper:

    def __init__(self):
        pass
    def scrapelinks(self):
        # Configuración Chrome
        options = Options()

        # options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        url = "https://gamesir.com/es/collections/all-products-1"

        print("Abriendo página...")
        driver.get(url)

        # Esperar carga inicial
        time.sleep(8)

        # Maximizar ventana
        driver.maximize_window()

        # Hacer la ventana muy alta
        driver.set_window_size(1920, 10000)

        # Eliminar posibles popups
        driver.execute_script("""
        document.querySelectorAll('*').forEach(el => {
            const style = window.getComputedStyle(el);

            if (
                style.position === 'fixed' &&
                parseInt(style.zIndex || 0) > 100
            ) {
                el.remove();
            }
        });
        """)

        # Zoom al 25%
        driver.execute_script(
            "document.body.style.zoom='1%'"
        )

        print("Esperando reorganización...")
        time.sleep(5)

        print("Iniciando carga completa de productos...")

        ultima_altura = 0

        for i in range(50):

            # Ir directamente al fondo
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            # Esperar que carguen más productos
            time.sleep(8)

            nueva_altura = driver.execute_script(
                "return document.body.scrollHeight"
            )

            print(
                f"Iteración {i+1} | Altura = {nueva_altura}"
            )

            if nueva_altura == ultima_altura:
                print("No se detectó más contenido")
                break

            ultima_altura = nueva_altura

        print("Espera final...")
        time.sleep(10)

        # Obtener HTML final
        html = driver.page_source

        # Guardar HTML
        with open(
            "gamesir_renderizado.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html)

        print("HTML guardado")

        # Parsear HTML
        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        productos = []

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if "/products/" in href:

                nombre = a.get_text(
                    " ",
                    strip=True
                )

                if href.startswith("/"):
                    href = "https://gamesir.com" + href

                productos.append({
                    "nombre": nombre,
                    "url": href
                })

        # Eliminar duplicados
        vistos = set()
        productos_finales = []

        for p in productos:

            if p["url"] not in vistos:

                vistos.add(p["url"])
                productos_finales.append(p)

        print(
            f"\nProductos encontrados: {len(productos_finales)}\n"
        )

        for p in productos_finales:

            print("Nombre:", p["nombre"])
            print("URL:", p["url"])
            print("-" * 60)

        # Guardar CSV
        df = pd.DataFrame(productos_finales)


        driver.quit()
        return df[["url"]]
    

    @staticmethod
    def obtener_producto(url):
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Nombre
        nombre = "No encontrado"
        h1 = soup.find("h1")
        if h1:
            nombre = h1.get_text(strip=True)

        # Precio
        precio = "No encontrado"

        selectores_precio = [
            ".price",
            ".price-item",
            "[class*=price]"
        ]

        for selector in selectores_precio:
            precio_tag = soup.select_one(selector)
            if precio_tag:
                precio = precio_tag.get_text(" ", strip=True)
                if precio:
                    break

        # Texto completo
        texto_completo = soup.get_text(" ", strip=True).lower()

        # Stock
        stock = "No encontrado"

        palabras_disponible = [
            "stock suficiente",
            "listo para enviar",
            "en stock",
            "disponible",
            "available",
            "in stock"
        ]

        palabras_agotado = [
            "agotado",
            "sin stock",
            "out of stock",
            "sold out"
        ]

        if any(p in texto_completo for p in palabras_disponible):
            stock = "Disponible"
        elif any(p in texto_completo for p in palabras_agotado):
            stock = "Agotado"

        # Colores
        colores = []

        for texto in soup.stripped_strings:
            texto = texto.strip()

            if texto.startswith("Color:"):
                color = texto.replace("Color:", "").strip()

                if color and color not in colores:
                    colores.append(color)

        # Descripción y Detalles desde accordion
        descripcion = ""
        detalles = ""

        for bloque in soup.select(".product-accordion.product-info-block"):
            summary = bloque.find("summary")
            if not summary:
                continue
            titulo = summary.get_text(strip=True).lower()
            partes = []
            for elem in summary.find_next_siblings():
                partes.append(elem.get_text(" ", strip=True))
            content = " ".join(partes).replace("\xa0", " ")
            if "description" in titulo:
                descripcion = content
            elif "details" in titulo:
                detalles = content

        # Imágenes
        imagenes = []

        for img in soup.find_all("img"):
            src = img.get("src")

            if not src:
                src = img.get("data-src")

            if src:
                if src.startswith("//"):
                    src = "https:" + src

                elif src.startswith("/"):
                    src = "https://gamesir.com" + src

                if src not in imagenes:
                    imagenes.append(src)

        # Productos relacionados
        relacionados = []

        for texto in soup.stripped_strings:

            if any(palabra in texto for palabra in [
                "Cooler",
                "GameSir",
                "Controller"
            ]):

                if texto not in relacionados:
                    relacionados.append(texto)

        return {
            "nombre": nombre,
            "precio": precio,
            "stock": stock,
            "colores": colores,
            "descripcion": descripcion,
            "detalles": detalles,
            "productos_relacionados": relacionados,
            "imagenes": imagenes,
            "link": url
        }
        #
    def nuevocsvdeproductos(self, urls=None):
        # Si no se pasan URLs, usa scrapeo normal
        if urls is None:
            links_df = self.scrapelinks()
            urls = links_df["url"].tolist()

        productos = []

        for url in urls:
            try:
                prod = self.obtener_producto(url)

                if not prod:
                    print(f"[SKIP] Producto vacío: {url}")
                    continue

                prod["colores"] = ", ".join(prod.get("colores", [])) if prod.get("colores") else ""
                prod["imagenes"] = " | ".join(prod.get("imagenes", [])) if prod.get("imagenes") else ""
                prod["productos_relacionados"] = " | ".join(prod.get("productos_relacionados", [])) if prod.get("productos_relacionados") else ""

                productos.append(prod)

            except Exception as e:
                print(f"[ERROR] No se pudo procesar {url} -> {e}")
                continue

        df = pd.DataFrame(productos)
        df.to_csv("productos_gamesir.csv", index=False, encoding="utf-8-sig")

        print(f"CSV guardado: {len(df)} productos en productos_gamesir.csv")
if __name__ == "__main__":
    print("Iniciando scraper...")
    gamesir = gamesir_scraper().nuevocsvdeproductos()
    #df = scraper.scrapelinks()
    #solo los url
    #for index, row in df.iterrows():
     #   print(f"{index+1}. {row['url']}")
        