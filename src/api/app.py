import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
import uvicorn
from services.scraping_x import main
from services.scraping_tiktok import main_tiktok
from services.scraping_face import main_facebook

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

@app.get("/scrape-x", tags=["web_scraping"], description="Scrape a webpage")
def scrape_webpage_x():
    main(100,5)
    
@app.get("/scrape-tik-tok", tags=["web_scraping"], description="Scrape a webpage")
def scrape_webpage_tiktok():
    main_tiktok()
        
@app.get("/scrape-facebook", tags=["web_scraping"], description="Scrape a webpage")
def scrape_webpage_facebook():
    main_facebook()

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=9999, reload=True)