import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv("api.env")

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

with open("notes.schema.json") as f:
    notes_schema = json.load(f)
with open("counters.schema.json") as f:
    counters_schema = json.load(f)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Create 'notes' collection with schema validation
try:
    db.create_collection(
        "notes",
        validator={"$jsonSchema": notes_schema},
        validationLevel="strict"
    )
    print("'notes' collection created with schema validation.")
except Exception as e:
    if "already exists" in str(e):
        print("'notes' collection already exists.")
    else:
        print(f"Error creating 'notes' collection: {e}")

# Create 'counters' collection with schema validation
try:
    db.create_collection(
        "counters",
        validator={"$jsonSchema": counters_schema},
        validationLevel="strict"
    )
    print("'counters' collection created with schema validation.")
except Exception as e:
    if "already exists" in str(e):
        print("'counters' collection already exists.")
    else:
        print(f"Error creating 'counters' collection: {e}") 