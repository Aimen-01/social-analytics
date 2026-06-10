from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db     = client["social_analytics"]

# collections
posts_col        = db["posts"]
users_col        = db["users"]
hashtags_col     = db["hashtag_stats"]
user_metrics_col = db["user_metrics"]
locks_col        = db["locks"]