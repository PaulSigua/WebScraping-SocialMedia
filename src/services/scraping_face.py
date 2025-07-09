import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import re
from glob import glob
import time
from dotenv import load_dotenv
import os
import re

# Tus credenciales (solo para pruebas, usa una cuenta secundaria)
load_dotenv()  # Carga variables del archivo .env

FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL")
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD")

# Configuración del navegador Chrome
options = Options()
options.add_argument("--disable-notifications")
# options.add_argument("--headless")  # Descomenta si no quieres que se abra ventana

def main_facebook():
    # Inicializa Chrome con WebDriverManager
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Ir a la página de login de Facebook
    driver.get("https://www.facebook.com/login")
    time.sleep(2)

    # Rellenar campos de login
    driver.find_element(By.ID, "email").send_keys(FACEBOOK_EMAIL)
    driver.find_element(By.ID, "pass").send_keys(FACEBOOK_PASSWORD + Keys.RETURN)

    # Confirmar que el login funcionó
    print("✅ Sesión iniciada en Facebook.")

    # Buscar el input de búsqueda usando aria-label
    time.sleep(5)
    search_input = driver.find_element(By.XPATH, '//input[@aria-label="Buscar en Facebook"]')
    search_input.send_keys("deportes")
    search_input.send_keys(Keys.RETURN)

    try:
        print("⏳ Buscando botón de 'Publicaciones'...")
        publicaciones_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "/search/posts/") and .//span[text()="Publicaciones"]]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", publicaciones_btn)
        publicaciones_btn.click()
        print(" Se hizo clic en el botón 'Publicaciones'")
        time.sleep(3)
    except Exception as e:
        print(f" No se pudo hacer clic en el botón 'Publicaciones': {type(e).__name__} - {e}")

    # Scroll inicial para cargar algunas publicaciones
    time.sleep(2)
    # Scroll para cargar resultados
    # Scroll para cargar resultados
    for _ in range(2):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

    def expandir_comentarios_hasta_completos(driver, total_objetivo, tiempo_espera=2, max_intentos=100):
        sin_cambios = 0
        anterior_total = 0

        for intento in range(max_intentos):
            comentarios_actuales = driver.find_elements(By.XPATH, '//div[@dir="auto" and contains(@style, "text-align: start")]')
            total_actual = len(comentarios_actuales)

            print(f" Intento {intento+1}: {total_actual}/{total_objetivo} comentarios visibles...")

            if total_actual >= total_objetivo:
                print(" Se alcanzó el total de comentarios esperados.")
                break

            if total_actual == anterior_total:
                sin_cambios += 1
            else:
                sin_cambios = 0

            if sin_cambios >= 3:
                print(" No hay nuevos comentarios después de varios intentos. Se detiene expansión.")
                break

            anterior_total = total_actual

            # Scroll hacia el último comentario visible
            if comentarios_actuales:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", comentarios_actuales[-1])
                except:
                    pass
            time.sleep(tiempo_espera)

            # Clic en "Ver más comentarios" o "Ver más respuestas"
            botones = driver.find_elements(By.XPATH, '//div[@role="button" and (contains(text(), "Ver más comentarios") or contains(text(), "Ver más respuestas"))]')
            for btn in botones:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(tiempo_espera)
                except Exception as e:
                    print(f" Error al hacer clic: {e}")

        print(" Finalizó expansión de comentarios.")


    # Procesar hasta 10 publicaciones (puedes aumentar el rango si quieres más)
    procesadas = 0
    while procesadas < 10:
        comentarios_btns = driver.find_elements(By.XPATH, '//span[text()="Comentar"]/ancestor::div[@role="button"]')

        if procesadas >= len(comentarios_btns):
            print(" No hay más publicaciones disponibles.")
            break

        try:
            print(f"\n Procesando publicación #{procesadas + 1}")
            btn = comentarios_btns[procesadas]

            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn)
            print(" Botón 'Comentar' clicado.")
            time.sleep(3)

            # Paso 1: Cambiar filtro a "Todos los comentarios" (solo si existe)
            try:
                menu_filtro = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Más pertinentes")]'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", menu_filtro)
                menu_filtro.click()
                time.sleep(1)

                opcion_todos = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Todos los comentarios")]'))
                )
                opcion_todos.click()
                print(" Se seleccionó la opción 'Todos los comentarios'")
                time.sleep(2)

            except Exception:
                print(" No se pudo cambiar el filtro de comentarios: puede que la publicación no tenga suficientes comentarios.")

            # Paso 2: Obtener número total de comentarios
            try:
                total_span = driver.find_element(By.XPATH, '//span[contains(text(), "comentario")]')
                texto = total_span.text
                numeros = [int(s) for s in texto.split() if s.isdigit()]
                total_comentarios_objetivo = numeros[0] if numeros else 0
                print(f" Se detectaron {total_comentarios_objetivo} comentarios en total.")
            except Exception as e:
                print(f" No se pudo obtener número de comentarios: {e}")
                total_comentarios_objetivo = 0

            # Validación: si no hay comentarios, pasar a la siguiente publicación
            if total_comentarios_objetivo == 0:
                print(" No hay comentarios para extraer. Se salta esta publicación.")
                procesadas += 1
                continue

            # Paso 3: Expandir todos los comentarios
            expandir_comentarios_hasta_completos(driver, total_comentarios_objetivo)

            # Paso 4: Extraer los comentarios visibles
            bloques_texto = driver.find_elements(By.XPATH, '//div[@dir="auto" and contains(@style, "text-align: start")]')
            comentarios_extraidos = []

            for bloque in bloques_texto:
                try:
                    texto = bloque.text.strip()
                    if texto:
                        comentarios_extraidos.append(texto)
                except Exception:
                    continue

            # Paso 5: Guardar CSV
            df = pd.DataFrame(comentarios_extraidos, columns=["Comentario"])
            df.to_csv(f"comentarios_publicacion_{procesadas + 1}.csv", index=False, encoding="utf-8-sig")
            print(f" Se guardaron {len(comentarios_extraidos)} comentarios en comentarios_publicacion_{procesadas + 1}.csv")

            # Paso 6: Cerrar la publicación
            try:
                cerrar_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Cerrar" or @aria-label="Cerrar publicación"]'))
                )
                cerrar_btn.click()
                print(" Publicación cerrada correctamente.")
            except Exception as e:
                print(f" No se pudo cerrar con botón: {e}")
                try:
                    from selenium.webdriver.common.keys import Keys
                    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    print(" Cerrada con tecla ESC.")
                except:
                    print(" Tampoco se pudo cerrar con ESC.")

            time.sleep(2)
            procesadas += 1

        except Exception as e:
            print(f" Error en publicación #{procesadas + 1}: {e}")
            time.sleep(1)
            procesadas += 1

    # Ruta donde están los CSV (cambia si están en otra carpeta)
    carpeta = '.'

    # Función para limpiar comentarios
    def limpiar_comentario(texto):
        if not isinstance(texto, str):
            return ""

        texto = re.sub(r"http\S+|www\S+", "", texto)  # eliminar URLs
        texto = re.sub(r"#\S+|@\S+", "", texto)       # eliminar hashtags y menciones
        texto = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s.,;!?¡¿]", "", texto)  # eliminar símbolos y emojis
        texto = re.sub(r"\s{2,}", " ", texto)         # eliminar espacios dobles
        return texto.strip()

    # Cargar todos los archivos CSV que empiecen por 'comentarios_publicacion_'
    archivos = glob(os.path.join(carpeta, "comentarios_publicacion_*.csv"))

    if not archivos:
        print(" No se encontraron archivos para procesar.")
    else:
        print(f" Archivos encontrados: {len(archivos)}")

        todos_los_comentarios = []

        for archivo in archivos:
            try:
                df = pd.read_csv(archivo)
                comentarios = df.iloc[:, 0].dropna().astype(str).tolist()
                todos_los_comentarios.extend(comentarios)
            except Exception as e:
                print(f" Error leyendo {archivo}: {e}")

        # Aplicar limpieza a todos los comentarios
        comentarios_limpios = [limpiar_comentario(c) for c in todos_los_comentarios if c.strip()]

        # Crear DataFrame final
        df_final = pd.DataFrame({
            "ComentarioCrudo": todos_los_comentarios,
            "ComentarioLimpio": comentarios_limpios
        })

        # Guardar el CSV final
        df_final.to_csv("comentarios_filtrados.csv", index=False, encoding="utf-8-sig")
        print(f" Se guardó el archivo combinado y filtrado: comentarios_filtrados.csv")

    # Esperamos un poco y luego cerramos
    time.sleep(10)

    #  Cerrar navegador
    # driver.quit()
    print(" Chrome cerrado correctamente.")