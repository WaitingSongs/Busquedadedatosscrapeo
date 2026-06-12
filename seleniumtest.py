from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Configuración Chrome
options = Options()

# Crear driver
driver = webdriver.Chrome(options=options)

# Abrir página
url = "https://gamesir.com/es/collections/all-products-1"
print("Abriendo navegador...")
driver.get(url)

# Esperar a que veas el navegador
time.sleep(30)

# Cerrar el navegador
driver.quit()
print("Navegador cerrado")
