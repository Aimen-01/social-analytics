from datetime import datetime, timedelta
from db import db

posts_col         = db["posts"]
hashtag_stats_col = db["hashtag_stats"]

WINDOWS = {
    "1h":  timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d":  timedelta(days=7)
}

def compute_trending(window="24h", limit=20):
    if window not in WINDOWS:
        raise ValueError(f"window must be one of {list(WINDOWS.keys())}")

    since = datetime.utcnow() - WINDOWS[window]

    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": since},
                "hashtags":   {"$ne": []}
            }
        },
        {"$unwind": "$hashtags"},
        {
            "$match": {
                "hashtags": {"$regex": "^[a-zA-Z][a-zA-Z0-9_]{1,}$"}
            }
        },
        {
            "$group": {
                "_id":            "$hashtags",
                "post_count":     {"$sum": 1},
                "total_likes":    {"$sum": "$metrics.likes"},
                "total_retweets": {"$sum": "$metrics.retweets"},
                "total_views":    {"$sum": "$metrics.views"},
                "unique_users":   {"$addToSet": "$user_id"}
            }
        },
        {
            "$addFields": {
                "unique_user_count": {"$size": "$unique_users"},
                "trend_score": {
                    "$add": [
                        "$post_count",
                        {"$multiply": ["$total_retweets", 3]},
                        {"$multiply": ["$total_likes", 1.5]}
                    ]
                }
            }
        },
        {"$project": {"unique_users": 0}},
        {"$sort": {"trend_score": -1}},
        {"$limit": limit}
    ]

    results = list(posts_col.aggregate(pipeline))

    computed_at = datetime.utcnow()
    for r in results:
        hashtag_stats_col.update_one(
            {"hashtag": r["_id"], "window": window},
            {"$set": {
                "hashtag":           r["_id"],
                "window":            window,
                "computed_at":       computed_at,
                "post_count":        r["post_count"],
                "total_likes":       r["total_likes"],
                "total_retweets":    r["total_retweets"],
                "total_views":       r["total_views"],
                "unique_user_count": r["unique_user_count"],
                "trend_score":       r["trend_score"]
            }},
            upsert=True
        )

    return results


def get_trending_cached(window="24h", limit=20):
    """
    Reads from materialized hashtag_stats if fresh (< 10 min).
    Falls back to running the pipeline if stale.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=10)

    cached = list(
        hashtag_stats_col
        .find({"window": window, "computed_at": {"$gte": cutoff}}, {"_id": 0})
        .sort("trend_score", -1)
        .limit(limit)
    )

    if cached:
        return {"source": "cache", "data": cached}

    results = compute_trending(window=window, limit=limit)
    clean = [{
        "hashtag":           r["_id"],
        "post_count":        r["post_count"],
        "total_likes":       r["total_likes"],
        "total_retweets":    r["total_retweets"],
        "unique_user_count": r["unique_user_count"],
        "trend_score":       round(r["trend_score"], 2)
    } for r in results]

    return {"source": "pipeline", "data": clean}