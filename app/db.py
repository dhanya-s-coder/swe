import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()
def get_database():
    return MongoClient(os.getenv('MONGODB_URI','mongodb://localhost:27017'),serverSelectionTimeoutMS=3000)[os.getenv('MONGODB_DATABASE','factory_simulation')]
def save_run(result, scenario):
    get_database().simulation_runs.insert_one({'created_at':datetime.now(timezone.utc),'result':result,'scenario':scenario})
