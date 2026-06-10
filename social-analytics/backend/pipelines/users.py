from datetime import datetime
from pymongo import UpdateOne
from db import db

posts_col        = db["posts"]
users_col        = db["users"]
user_metrics_col = db["user_metrics"]


def compute_user_metrics(limit=100):
    """
    Multi-stage $lookup pipeline joining posts → users.
    Computes per-user engagement stats and influence score.
    Writes results to user_metrics collection.
    """
    pipeline = [
        {
            "$group": {
                "_id":            "$user_id",
                "post_count":     {"$sum": 1},
                "total_likes":    {"$sum": "$metrics.likes"},
                "total_retweets": {"$sum": "$metrics.retweets"},
                "total_replies":  {"$sum": "$metrics.replies"},
                "total_views":    {"$sum": "$metrics.views"},
                "avg_likes":      {"$avg": "$metrics.likes"},
                "avg_retweets":   {"$avg": "$metrics.retweets"},
                "latest_post":    {"$max": "$created_at"},
                "platforms":      {"$addToSet": "$platform"}
            }
        },
        {
            "$lookup": {
                "from":         "users",
                "localField":   "_id",
                "foreignField": "user_id",
                "as":           "user_info"
            }
        },
        {
            "$unwind": {
                "path":                       "$user_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$addFields": {
                "followers": {
                    "$ifNull": ["$user_info.followers_count", 1]
                },
                "engagement_rate": {
                    "$cond": {
                        "if":   {"$gt": ["$total_views", 0]},
                        "then": {
                            "$divide": [
                                {"$add": [
                                    "$total_likes",
                                    "$total_retweets",
                                    "$total_replies"
                                ]},
                                "$total_views"
                            ]
                        },
                        "else": 0
                    }
                },
                "viral_coefficient": {
                    "$cond": {
                        "if":   {"$gt": ["$total_likes", 0]},
                        "then": {"$divide": ["$total_retweets", "$total_likes"]},
                        "else": 0
                    }
                }
            }
        },
        {
            "$addFields": {
                "influence_score": {
                    "$add": [
                        {"$multiply": [
                            {"$ln": {"$max": ["$followers", 1]}}, 10
                        ]},
                        {"$multiply": ["$engagement_rate",   500]},
                        {"$multiply": ["$viral_coefficient",  30]},
                        {"$multiply": ["$post_count",         0.5]}
                    ]
                }
            }
        },
        {"$sort":  {"influence_score": -1}},
        {"$limit": limit},
        {
            "$project": {
                "user_id":           "$_id",
                "username":          "$user_info.username",
                "followers":         1,
                "verified":          "$user_info.verified",
                "post_count":        1,
                "avg_likes":         1,
                "avg_retweets":      1,
                "total_views":       1,
                "total_likes":       1,
                "total_retweets":    1,
                "engagement_rate":   1,
                "viral_coefficient": 1,
                "influence_score":   1,
                "latest_post":       1,
                "platforms":         1
            }
        }
    ]

    results = list(posts_col.aggregate(pipeline))

    computed_at = datetime.utcnow()
    ops = []
    for rank, r in enumerate(results, start=1):
        r["influence_rank"] = rank
        r["computed_at"]    = computed_at
        ops.append(UpdateOne(
            {"user_id": r["user_id"]},
            {"$set": r},
            upsert=True
        ))

    if ops:
        user_metrics_col.bulk_write(ops, ordered=False)

    return results


def get_top_users(limit=10):
    """Fast read from pre-computed user_metrics collection."""
    return list(
        user_metrics_col
        .find({}, {"_id": 0})
        .sort("influence_rank", 1)
        .limit(limit)
    )