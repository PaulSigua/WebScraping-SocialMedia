from services.driver import get_chrome_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time, os
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("TWITTER_EMAIL")
PASSWORD = os.getenv("TWITTER_PASSWORD")
USERNAME = os.getenv("TWITTER_USERNAME")

def open_twitter_login(driver):
    driver = get_chrome_driver()
    driver.get("https://x.com/i/flow/login")
    time.sleep(3)

    email_input = driver.find_element(By.NAME, "text")
    email_input.send_keys(EMAIL)
    email_input.send_keys(Keys.RETURN)
    time.sleep(3)
    
    email_input = driver.find_element(By.NAME, "text")
    email_input.send_keys(USERNAME)
    email_input.send_keys(Keys.RETURN)
    time.sleep(3)


    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

    print("Sesión iniciada exitosamente")
    
    return driver

def go_to_explore(driver):
    wait = WebDriverWait(driver, 15)

    explore_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="/explore" and @role="link"]'))
    )
    explore_btn.click()
    print("✅ Navegación a la sección 'Explorar' completada")
    
def search_keyword(driver, keyword):
    wait = WebDriverWait(driver, 15)

    search_input = wait.until(
        EC.presence_of_element_located((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]'))
    )
    search_input.clear()
    search_input.send_keys(keyword)
    search_input.send_keys(Keys.RETURN)
    print(f"🔍 Búsqueda realizada: {keyword}")
    time.sleep(5)
    
def extract_tweet_texts(driver, max_count):
    wait = WebDriverWait(driver, 10)

    # Esperar a que al menos un tweet esté presente
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetText"]')))

    tweets = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')

    print(f"\n🟦 Tweets encontrados: {len(tweets)}")
    print("📝 Contenido de los tweets:\n")

    extracted = []

    for i, tweet in enumerate(tweets[:max_count], 1):
        text = tweet.text.strip()
        extracted.append(text)
        print(f"{i}. {text}\n")

    return extracted