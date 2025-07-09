# webscraping/scraping.py
import os, time, pandas as pd, subprocess, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from services.limpieza import LimpiezaComentarios

class ScraperTikTok:
    def __init__(self, palabra_clave="mundial de clubes", max_videos=10):
        self.palabra_clave = palabra_clave
        self.max_videos = max_videos
        self.comentarios_data = []
        self.urls = []

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-webrtc")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)

    def buscar_videos(self):
        self.driver.get("https://www.tiktok.com/")
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-e2e="nav-search"]'))
        )

        btn_lupa = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="nav-search"]'))
        )
        btn_lupa.click()
        time.sleep(2)

        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[data-e2e="search-user-input"]')
        input_search = next((i for i in inputs if i.is_displayed() and i.is_enabled()), None)
        if not input_search:
            self.driver.quit()
            raise Exception("No se encontró el input de búsqueda.")

        input_search.click()
        input_search.clear()
        input_search.send_keys(self.palabra_clave)
        input_search.send_keys(Keys.ENTER)
        time.sleep(4)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "/video/")]'))
        )

        videos = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/video/")]')
        for v in videos:
            href = v.get_attribute("href")
            if href and href not in self.urls:
                self.urls.append(href)
            if len(self.urls) >= self.max_videos:
                break

    def extraer_comentarios(self):
        for url in self.urls:
            print(f"🔗 Extrayendo de: {url}")
            self.driver.get(url)
            time.sleep(2)

            last_count = 0
            same_count_retries = 0
            max_retries = 5
            max_scrolls = 10
            scrolls = 0

                        #Pausar el video con el botón SVG
            try:
                pausa_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.css-q1bwae-DivPlayIconContainer'))
                )
                pausa_btn.click()
                print("Video pausado mediante botón.")
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ No se pudo pausar el video: {e}")

            while same_count_retries < max_retries and scrolls < max_scrolls:
                self.driver.execute_script("window.scrollBy(0, 700)")
                time.sleep(4)

                if "/video/" not in self.driver.current_url:
                    print("Saliste del video, recargando...")
                    self.driver.get(url)
                    time.sleep(10)
                    last_count = 0
                    same_count_retries = 0
                    continue

                items = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="DivCommentContentWrapper"]')
                current_count = len(items)
                print(f"Comentarios visibles: {current_count}")

                if current_count == last_count:
                    same_count_retries += 1
                else:
                    same_count_retries = 0
                    last_count = current_count

                scrolls += 1

            print(f"Scroll finalizado. Total comentarios detectados: {last_count}")

            try:
                WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="DivCommentContentWrapper"]'))
                )
                items = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="DivCommentContentWrapper"]')
            except:
                print("No se encontraron comentarios después del scroll.")
                continue

            for item in items:
                try:
                    usuario_elem = item.find_element(By.CSS_SELECTOR, 'a[href*="/@"]')
                    comentario_elem = item.find_element(By.CSS_SELECTOR, 'span[data-e2e^="comment-level"] p')
                    usuario = usuario_elem.text.strip()
                    comentario = comentario_elem.text.strip()
                    if re.search(r"\b\w+\b", comentario):
                        self.comentarios_data.append({"usuario": usuario, "comentario": comentario})
                except:
                    continue


    def guardar_csv(self, ruta="comentarios_tiktok.csv"):
        df = pd.DataFrame(self.comentarios_data)
        df.to_csv(ruta, index=False, encoding="utf-8")
        print(f"Comentarios guardados en {ruta}")
        self.driver.quit()


def main_tiktok():
    print("Iniciando scraping de TikTok...")
    scraper = ScraperTikTok(palabra_clave="mundial de clubes 2025", max_videos=10)
    scraper.buscar_videos()
    scraper.extraer_comentarios()
    scraper.guardar_csv()

    print("\nIniciando limpieza de comentarios...")
    time.sleep(2)
    limpieza = LimpiezaComentarios("comentarios_tiktok.csv")
    limpieza.procesar("comentarios_tiktok_limpio.csv")

    print("\nProceso completo finalizado.")