#Video De youtube donde se explica el funcionamiento 



https://github.com/user-attachments/assets/c310ec59-95e6-42a2-aeb6-c61d39d3d36d







# GameSir Product Scraper & Analytics

Proyecto de scraping dinámico, limpieza de datos, visualización y modelado predictivo sobre el catálogo de productos GameSir.

## Estructura del proyecto

```
├── app.py                         # Dashboard Streamlit con filtros y predicción
├── Libraries/
│   ├── __init__.py
│   ├── scraper.py                 # Scraping dinámico con Selenium + BeautifulSoup
│   ├── limpieza.py                # Limpieza, transformación y análisis exploratorio
│   └── prediccion.py              # Modelo predictivo (Random Forest + GridSearchCV)
├── productos_gamesir.csv          # Datos crudos del scraping
├── productos_limpios.csv          # Datos limpios listos para usar
└── gamesir_renderizado.html       # HTML renderizado capturado por Selenium
```

## Flujo del pipeline

1. **Scraping** → `scraper.py` usa Selenium para navegar la colección de GameSir, hace scroll infinito (hasta 50 iteraciones), extrae URLs de cada producto y luego visita cada uno para obtener nombre, precio, stock, colores, descripción, imágenes, etc.
2. **Limpieza** → `limpieza.py` parsea precios a numéricos, maneja nulos (colores sin variante, stock no encontrado), clasifica productos por tipo (Control/Accesorio/Cable/Enfriamiento), asigna gama de precio (Económica/Media/Alta/Premium), concatenación masiva con datos externos y filtros agrupados.
3. **Predicción** → `prediccion.py` entrena un RandomForestClassifier con GridSearchCV para predecir la gama de cada producto basándose en características como tipo, cantidad de colores, longitud de descripción, stock y si está en oferta.
4. **Visualización** → `app.py` muestra el catálogo en Streamlit con filtros por texto, tipo y gama, más una tabla comparativa de gama real vs predicha.

## Requisitos

- Python 3.14+
- Chrome/Chromium + chromedriver
- Dependencias: `streamlit`, `pandas`, `selenium`, `beautifulsoup4`, `requests`, `scikit-learn`, `joblib`

## Cómo ejecutar

```bash
streamlit run app.py
```

Desde la interfaz se puede presionar "Actualizar datos desde la web" para ejecutar el pipeline completo (scraping → limpieza → predicción).

## Ejecución individual

```bash
.venv/bin/python3 Libraries/scraper.py
.venv/bin/python3 Libraries/limpieza.py
.venv/bin/python3 Libraries/prediccion.py
```
