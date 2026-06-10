import pandas as pd
import re
from pymongo import MongoClient, UpdateOne
from datetime import datetime, timedelta
from textblob import TextBlob
import random
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db     = client["social_analytics"]

posts_col        = db["posts"]
users_col        = db["users"]
hashtags_col     = db["hashtag_stats"]
user_metrics_col = db["user_metrics"]
locks_col        = db["locks"]

# ── Helpers ──────────────────────────────────────────────
def extract_hashtags(text):
    return [t.lower() for t in re.findall(r"#(\w+)", text)]

def extract_mentions(text):
    return [m.lower() for m in re.findall(r"@(\w+)", text)]

def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def generate_metrics(followers):
    base      = max(1, followers // 1000)
    likes     = random.randint(0, base * 50)
    retweets  = random.randint(0, max(1, likes // 3))
    replies   = random.randint(0, max(1, likes // 5))
    views     = likes * random.randint(8, 25)
    return {"likes": likes, "retweets": retweets,
            "replies": replies, "views": views}

def get_sentiment(text):
    score = TextBlob(str(text)).sentiment.polarity
    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"
    return {"score": round(score, 4), "label": label}

PLATFORMS  = ["Twitter/X", "Instagram", "Facebook", "YouTube"]
POST_TYPES = ["text", "image", "video", "reel"]
PT_WEIGHTS = [0.40, 0.30, 0.20, 0.10]

# ── Load CSV ─────────────────────────────────────────────
print("Loading dataset...")
cols = ["sentiment", "post_id", "created_at_raw", "query", "username", "text"]
df = pd.read_csv(
    "data/training.1600000.processed.noemoticon.csv",
    encoding="latin-1",
    header=None,
    names=cols
)

df = df.sample(n=100_000, random_state=42).reset_index(drop=True)
df["text"] = df["text"].astype(str)
print(f"Loaded {len(df)} rows")

# ── Build users ───────────────────────────────────────────
print("Building users...")
unique_users = df["username"].unique()
user_map     = {}
user_docs    = []

for uname in unique_users:
    uid = f"u_{abs(hash(uname)) % 10_000_000:07d}"
    roll = random.random()
    if roll < 0.70:
        followers = random.randint(10, 500)
    elif roll < 0.92:
        followers = random.randint(500, 10_000)
    else:
        followers = random.randint(10_000, 500_000)

    user_map[uname] = {"uid": uid, "followers": followers}
    user_docs.append({
        "user_id":         uid,
        "username":        uname,
        "followers_count": followers,
        "following_count": random.randint(50, min(5000, followers + 200)),
        "verified":        followers > 100_000 and random.random() > 0.6,
        "created_at":      random_date(datetime(2008, 1, 1), datetime(2022, 1, 1))
    })

# ── Bulk Writing Users in Batches (Fixes MaxTimeMSExpired Timeout Error) ──
print(f"Preparing {len(user_docs)} user write operations...")
ops = [
    UpdateOne({"user_id": u["user_id"]}, {"$setOnInsert": u}, upsert=True)
    for u in user_docs
]

print("Inserting users into MongoDB in batches...")
user_chunk_size = 2000
for i in range(0, len(ops), user_chunk_size):
    chunk = ops[i:i + user_chunk_size]
    try:
        users_col.bulk_write(chunk, ordered=False)
        print(f"  Processed {min(i + user_chunk_size, len(ops))}/{len(ops)} users...")
    except Exception as e:
        print(f"  Warning encountered during batch insert: {e}")

print("Users sync operation done.")

# ── Build posts ───────────────────────────────────────────
print("Building posts... (this takes a few minutes due to TextBlob)")
start_date = datetime(2023, 1, 1)
end_date   = datetime(2024, 6, 1)
post_docs  = []

for i, row in df.iterrows():
    if i % 10_000 == 0:
        print(f"   Processing {i}/{len(df)}...")

    uname     = row["username"]
    uid       = user_map[uname]["uid"]
    followers = user_map[uname]["followers"]
    text      = row["text"]

    post_docs.append({
        "post_id":  str(row["post_id"]),
        "text":       text,
        "user_id":    uid,
        "username":   uname,
        "created_at": random_date(start_date, end_date),
        "hashtags":   extract_hashtags(text),
        "mentions":   extract_mentions(text),
        "platform":   random.choice(PLATFORMS),
        "post_type":  random.choices(POST_TYPES, weights=PT_WEIGHTS, k=1)[0],
        "sentiment":  get_sentiment(text),
        "lang":       "en",
        "version":    1,
        "metrics":    generate_metrics(followers)
    })

# ── Insert in batches ─────────────────────────────────────
print("Inserting posts into MongoDB...")
chunk_size = 5_000
for i in range(0, len(post_docs), chunk_size):
    chunk = post_docs[i:i + chunk_size]
    posts_col.insert_many(chunk, ordered=False)
    print(f"   Inserted {min(i + chunk_size, len(post_docs))}/{len(post_docs)}")

# ── Indexes ───────────────────────────────────────────────
print("Creating indexes...")
posts_col.create_index([("hashtags", 1), ("created_at", -1)])
posts_col.create_index([("user_id",  1), ("created_at", -1)])
posts_col.create_index([("platform", 1), ("created_at", -1)])
posts_col.create_index([("metrics.likes", -1)])
posts_col.create_index([("sentiment.label", 1)])
posts_col.create_index([("created_at", -1)])
hashtags_col.create_index([("hashtag", 1), ("window", 1)])
hashtags_col.create_index([("computed_at", 1)], expireAfterSeconds=86400)
locks_col.create_index([("resource_id", 1)], unique=True)
locks_col.create_index([("created_at", 1)], expireAfterSeconds=30)
print("Indexes done.")

print("\nIngestion complete!")
print(f"   Posts : {posts_col.count_documents({})}")
print(f"   Users : {users_col.count_documents({})}")