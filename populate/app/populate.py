######## Populate #######
import os
import numpy as np
import pandas as pd
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

from date_control import format_date

load_dotenv()

MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST")

file = "../data/gallica_presse_1.parquet"
client = MongoClient(f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongo")

db = client["gallica"]
articles = db.presse_articles

for article in articles.find():
    pprint(article)

df_articles = pd.read_parquet(file)

df_articles["date"] = df_articles["date"].apply(format_date)

articles_dict = df_articles.to_dict(orient="records")

# for art in articles_dict:
#     post_id = articles.insert_one(art).inserted_id
#     print(post_id)