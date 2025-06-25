import os
from pymongo import MongoClient
import time
from dotenv import load_dotenv

# Load environment variables from api.env file
load_dotenv("api.env")

_client = None
_db = None

def connect_to_db(retries=3, delay=2):
    global _client, _db
    if _client is None:
        mongo_url = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
        for attempt in range(retries):
            try:
                _client = MongoClient(mongo_url)
                _db = _client.get_default_database()
                if _db is None:
                    _db = _client[os.getenv("MONGO_DB_NAME", "ai_notes")]
                break
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to connect to MongoDB after {retries} attempts: {e}")
    return _db

def get_next_note_id(db):
    counters = db["counters"]
    result = counters.find_one_and_update(
        {"_id": "note_id"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result["seq"]