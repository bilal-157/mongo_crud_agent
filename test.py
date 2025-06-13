from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client[os.getenv('MONGO_DB')]
    print("Collections in database:", db.list_collection_names())
    client.close()
except Exception as e:
    print("Connection failed:", e)