# Busqueda de datos / Scraping GameSir

Este proyecto contiene ejemplos de extracción de datos y visualización de un catálogo de productos GameSir.

## Qué hace cada archivo

- `app.py`
  - Aplicación web creada con Streamlit.
  - Carga `productos_gamesir.csv` y muestra los productos en una interfaz con filtros de búsqueda y categoría.
  - Muestra precio, stock, colores, descripción, detalles e imágenes.

- `seleniumtest.py`
  - Define la clase `gamesir_scraper` para extraer enlaces de productos desde la página de colección de GameSir.
  - Usa Selenium para renderizar la página, hacer scroll automático y guardar el HTML en `gamesir_renderizado.html`.
  - Extrae los enlaces de productos y devuelve un DataFrame con las URLs.

- `test.py`
  - Script de prueba que usa Requests y BeautifulSoup para leer una página de producto.
  - Extrae bloques de texto de descripción y detalles.

- `main.py`
  - Ejemplo simple de uso de Selenium para abrir la página de productos y cerrar el navegador.

## Requisitos de Python

Las librerías necesarias actualmente son:

- `streamlit`
- `pandas`
- `selenium`
- `beautifulsoup4`
- `requests`

## Requisitos adicionales

- Navegador Chrome o Chromium instalado.
- `chromedriver` compatible con la versión de Chrome/Chromium.
- El driver debe estar en el `PATH` o configurado para que Selenium pueda acceder a él.

## Cómo ejecutar

1. Instalar dependencias:

```bash
python -m pip install streamlit pandas selenium beautifulsoup4 requests
```

2. Ejecutar la aplicación Streamlit:

```bash
cd /home/melody/Documentos/Code/Homework/Busquedadedatosscrapeo
streamlit run app.py
```

3. Ejecutar el scraper de enlaces con Selenium:

```bash
python seleniumtest.py
```

> Nota: `seleniumtest.py` define la clase `gamesir_scraper`; para usarla deberás crear una instancia y llamar a `scrapelinks()` desde otro script o desde un intérprete.

## Observaciones

- El archivo `productos_gamesir.csv` ya contiene los productos que muestra `app.py`.
- El scraper necesita tiempo de carga y puede depender de cambios en el HTML del sitio.
