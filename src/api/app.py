import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
import uvicorn, time
from services.driver import get_chrome_driver
from services.scraping import open_twitter_login, go_to_explore, search_keyword, extract_tweet_texts

app = FastAPI(
    title="Web Scraping API",
    description="API for web scraping tasks using Selenium, BeautifulSoup, and Pandas.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "web_scraping",
            "description": "Endpoints for web scraping operations."
        }
    ]
)

@app.get("/", tags=["web_scraping"], description="Root default")
async def read_root():
    """
    Root endpoint for the Web Scraping API.
    Returns a welcome message.
    """
    return {"message": "Welcome to the Web Scraping API!"}

@app.get("/scrape", tags=["web_scraping"], description="Scrape a webpage")
def scrape_webpage():
    driver_ = get_chrome_driver()
    driver = open_twitter_login(driver_)
    time.sleep(2)
    go_to_explore(driver)
    search_keyword(driver,"mundial de clubes")
    extract_tweet_texts(driver, 10)
    

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=9999)