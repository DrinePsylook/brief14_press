import os
import logging
import uvicorn
from datetime import datetime
from typing import List, Annotated, Optional
from pydantic import BaseModel, BeforeValidator, Field
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

client = AsyncIOMotorClient(f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongo")
db = client.get_database("gallica")
articles_collection = db.get_collection("presse_articles")

PyObjectId = Annotated[str, BeforeValidator(str)]

class ArticlesModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    file_id: str
    title: str
    date: datetime
    author: str
    page_count: int
    complete_text: str

class DateRange(BaseModel):
    min_date: Optional[datetime] = None
    max_date: Optional[datetime] = None

async def test_mongodb_connection():
    try:
        await client.admin.command('ping')
        logging.info("Connexion MongoDB réussie !")
    except Exception as e:
        logging.error(f"Erreur de connexion MongoDB : {e}")

@app.on_event("startup")
async def startup_event():
    await test_mongodb_connection()

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get(
    "/articles", 
    response_description = "List all articles",
    response_model=List[ArticlesModel],
    response_model_by_alias=False
    )
async def read_articles():
    """
    List all articles
    The response is unpaginated and limited to 10 results
    """ 
    logging.info(f"MONGO_USERNAME: {MONGO_USERNAME}")
    logging.info(f"MONGO_PASSWORD: {MONGO_PASSWORD}")
    articles = []
    try:
        async for article in articles_collection.find().limit(2):
            articles.append(ArticlesModel(**article))
        return articles
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des articles: {e}")
        raise


@app.get("/dates", response_model=DateRange)
async def get_dates_minmax():
    """Find min and max dates"""
    dates = []
    try:
        pipeline = [
            {"$group": {
                "_id": None,
                "min_date": {"$min": "$date"},
                "max_date": {"$max": "$date"}
                }
            }
        ]
        result = await articles_collection.aggregate(pipeline).to_list(length=1)
        if result:
            return DateRange(min_date=result[0].get("min_date"), max_date=result[0].get("max_date"))
        else:
            return DateRange()
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des dates min/max: {e}")
        raise

@app.get("/dates_choice/{date_min}/{date_max}")
async def get_art_dates(date_min: str, date_max: str) -> List[dict]:
    """
        Display articles between 2 dates
    """
    articles = []
    try:
        date_min_obj = datetime.strptime(date_min, "%Y-%m-%d")
        date_max_obj = datetime.strptime(date_max, "%Y-%m-%d")
        
        query = {
            "date": {
                "$gte": date_min_obj,
                "$lte": date_max_obj
            }
        }
        articles = await articles_collection.find(query).to_list(length=None)
        return articles
    except ValueError as e:
        return {"error": f"Format de date invalide : {e}"}
    except Exception as e:
        return {"error": f"Une erreur est survenue : {e}"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)