from flask import Blueprint, jsonify, request
from db import posts_col, users_col

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/stats")
def get_stats():
    total_posts = posts_col.count_documents({})
    total_users = users_col.count_documents({})

    pipeline = [
        {"$group": {
            "_id": None,
            "total_likes":    {"$sum": "$metrics.likes"},
            "total_retweets": {"$sum": "$metrics.retweets"},
            "total_views":    {"$sum": "$metrics.views"}
        }}
    ]
    result = list(posts_col.aggregate(pipeline))
    totals = result[0] if result else {}

    return jsonify({
        "total_posts":    total_posts,
        "total_users":    total_users,
        "total_likes":    totals.get("total_likes", 0),
        "total_retweets": totals.get("total_retweets", 0),
        "total_views":    totals.get("total_views", 0)
    })


@dashboard_bp.route("/platforms")
def get_platforms():
    pipeline = [
        {"$group": {
            "_id":         "$platform",
            "post_count":  {"$sum": 1},
            "total_likes": {"$sum": "$metrics.likes"}
        }},
        {"$sort": {"post_count": -1}}
    ]
    results = list(posts_col.aggregate(pipeline))
    return jsonify({"data": [
        {"platform": r["_id"], "post_count": r["post_count"], "total_likes": r["total_likes"]}
        for r in results
    ]})


@dashboard_bp.route("/sentiment")
def get_sentiment():
    pipeline = [
        {"$group": {
            "_id":   "$sentiment.label",
            "count": {"$sum": 1}
        }}
    ]
    results = list(posts_col.aggregate(pipeline))
    return jsonify({"data": [
        {"label": r["_id"], "count": r["count"]}
        for r in results if r["_id"]
    ]})


@dashboard_bp.route("/sharding-info")
def sharding_info():
    return jsonify({
        "concept": "Horizontal Scaling with MongoDB Sharding",
        "shard_key": "platform",
        "reason": "Distributes posts across shards by platform for parallel queries",
        "collections": ["posts", "users"],
        "benefits": [
            "Handles 10M+ posts without performance degradation",
            "Each platform's data lives on dedicated shard",
            "Queries filtered by platform hit only one shard"
        ],
        "atlas_config": {
            "tier": "M0 Free (demo)",
            "upgrade_path": "M10+ enables actual sharding",
            "replica_set": "3 nodes already configured"
        }
    })