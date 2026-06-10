from datetime import datetime, timedelta
from db import db

posts_col = db["posts"]

WINDOWS = {
    "1h":  timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d":  timedelta(days=7),
    "30d": timedelta(days=30)
}

def compute_viral_posts(window="7d", limit=50):
    """
    Ranks posts by viral coefficient.
    Viral coefficient = retweets / max(likes, 1)
    Score > 1 means spreading faster than it accumulates likes.
    """
    since = datetime.utcnow() - WINDOWS.get(window, WINDOWS["24h"])

    pipeline = [
        {
            "$match": {
                "created_at":    {"$gte": since},
                "metrics.likes": {"$gt": 0}
            }
        },
        {
            "$addFields": {
                "viral_coefficient": {
                    "$divide": [
                        "$metrics.retweets",
                        {"$max": ["$metrics.likes", 1]}
                    ]
                },
                "engagement_rate": {
                    "$divide": [
                        {
                            "$add": [
                                "$metrics.likes",
                                "$metrics.retweets",
                                "$metrics.replies"
                            ]
                        },
                        {"$max": ["$metrics.views", 1]}
                    ]
                }
            }
        },
        {
            "$addFields": {
                "composite_score": {
                    "$add": [
                        {"$multiply": ["$viral_coefficient", 40]},
                        {"$multiply": ["$engagement_rate", 60]}
                    ]
                }
            }
        },
        {"$sort": {"composite_score": -1}},
        {"$limit": limit},
        {
            "$project": {
                "post_id":           1,
                "text":              1,
                "username":          1,
                "platform":          1,
                "post_type":         1,
                "created_at":        1,
                "hashtags":          1,
                "sentiment":         1,
                "metrics":           1,
                "viral_coefficient": 1,
                "engagement_rate":   1,
                "composite_score":   1
            }
        }
    ]

    return list(posts_col.aggregate(pipeline))


def get_engagement_over_time(hashtag=None, window="7d"):
    """
    Returns post counts + avg engagement bucketed by day.
    Used for the time-series chart on the dashboard.
    """
    since = datetime.utcnow() - WINDOWS.get(window, WINDOWS["7d"])

    match_stage = {"created_at": {"$gte": since}}
    if hashtag:
        match_stage["hashtags"] = hashtag.lower()

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": {
                    "year":  {"$year":         "$created_at"},
                    "month": {"$month":        "$created_at"},
                    "day":   {"$dayOfMonth":   "$created_at"}
                },
                "post_count":   {"$sum": 1},
                "avg_likes":    {"$avg": "$metrics.likes"},
                "avg_retweets": {"$avg": "$metrics.retweets"},
                "total_views":  {"$sum": "$metrics.views"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
    ]

    raw = list(posts_col.aggregate(pipeline))

    return [{
        "date":         f"{r['_id']['year']}-{r['_id']['month']:02d}-{r['_id']['day']:02d}",
        "post_count":   r["post_count"],
        "avg_likes":    round(r["avg_likes"], 1),
        "avg_retweets": round(r["avg_retweets"], 1),
        "total_views":  r["total_views"]
    } for r in raw]


def get_engagement_heatmap():
    """
    Returns post counts bucketed by day-of-week x hour-of-day.
    Produces a 7x24 matrix normalised 0-10 for the heatmap panel.
    """
    pipeline = [
        {
            "$group": {
                "_id": {
                    "day":  {"$dayOfWeek": "$created_at"},
                    "hour": {"$hour":      "$created_at"}
                },
                "post_count":     {"$sum": 1},
                "total_likes":    {"$sum": "$metrics.likes"},
                "total_retweets": {"$sum": "$metrics.retweets"}
            }
        },
        {
            "$addFields": {
                "engagement_score": {
                    "$add": [
                        "$post_count",
                        {"$multiply": ["$total_likes",    0.5]},
                        {"$multiply": ["$total_retweets", 1.5]}
                    ]
                }
            }
        },
        {"$sort": {"_id.day": 1, "_id.hour": 1}}
    ]

    raw = list(posts_col.aggregate(pipeline))

    matrix = [[0] * 24 for _ in range(7)]
    for r in raw:
        d = r["_id"]["day"] - 1
        h = r["_id"]["hour"]
        matrix[d][h] = r["engagement_score"]

    max_score = max(
        matrix[d][h] for d in range(7) for h in range(24)
    ) or 1

    for d in range(7):
        for h in range(24):
            matrix[d][h] = round(matrix[d][h] / max_score * 10, 2)

    return matrix


def get_sentiment_breakdown():
    """
    Returns count of positive / neutral / negative posts.
    """
    pipeline = [
        {
            "$group": {
                "_id":       "$sentiment.label",
                "count":     {"$sum": 1},
                "avg_score": {"$avg": "$sentiment.score"}
            }
        }
    ]
    results = list(posts_col.aggregate(pipeline))
    return [
        {
            "label":     r["_id"],
            "count":     r["count"],
            "avg_score": round(r["avg_score"], 4)
        }
        for r in results if r["_id"]
    ]