from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from bson import ObjectId
from datetime import datetime

from db import posts_col
from backend.pipelines.transactions import create_post_with_transaction
from pipelines.concurrency  import acquire_lock, release_lock, check_lock
from pipelines.engagement   import (
    compute_viral_posts,
    get_engagement_over_time,
    get_engagement_heatmap,
    get_sentiment_breakdown
)

posts_bp = Blueprint("posts", __name__)


def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


def serialize(doc):
    doc["_id"] = str(doc["_id"])
    for key in ["created_at", "updated_at"]:
        if key in doc and hasattr(doc[key], "isoformat"):
            doc[key] = doc[key].isoformat()
    for key in ["viral_coefficient", "engagement_rate", "composite_score"]:
        if key in doc:
            doc[key] = round(float(doc[key]), 4)
    return doc


@posts_bp.route("/")
def get_posts():
    """
    GET /api/posts/?platform=Instagram&limit=20
    Returns top posts sorted by likes, optionally filtered by platform.
    """
    platform = request.args.get("platform")
    limit    = int(request.args.get("limit", 20))
    query    = {}
    if platform:
        query["platform"] = platform
    posts = list(posts_col.find(query).sort("metrics.likes", -1).limit(limit))
    return jsonify({"data": [serialize(p) for p in posts]})


@posts_bp.route("/viral")
def viral():
    """
    GET /api/posts/viral?window=24h&limit=20
    Returns top posts ranked by viral coefficient.
    """
    window = request.args.get("window", "7d")
    limit  = int(request.args.get("limit", 20))
    results = compute_viral_posts(window=window, limit=limit)
    return jsonify({"data": [serialize(r) for r in results]})


@posts_bp.route("/timeline")
def timeline():
    """
    GET /api/posts/timeline?window=7d&hashtag=tech
    Returns daily post counts + engagement for charting.
    """
    window  = request.args.get("window", "7d")
    hashtag = request.args.get("hashtag", None)
    results = get_engagement_over_time(hashtag=hashtag, window=window)
    return jsonify({"data": results})


@posts_bp.route("/heatmap")
def heatmap():
    """
    GET /api/posts/heatmap
    Returns 7x24 engagement matrix for heatmap panel.
    """
    return jsonify({"data": get_engagement_heatmap()})


@posts_bp.route("/sentiment")
def sentiment():
    """
    GET /api/posts/sentiment
    Returns positive / neutral / negative breakdown.
    """
    return jsonify({"data": get_sentiment_breakdown()})


@posts_bp.route("/stats")
def stats():
    """
    GET /api/posts/stats
    Returns overall collection totals for dashboard header cards.
    """
    total_posts = posts_col.count_documents({})
    pipeline = [{
        "$group": {
            "_id":            None,
            "total_likes":    {"$sum": "$metrics.likes"},
            "total_retweets": {"$sum": "$metrics.retweets"},
            "total_views":    {"$sum": "$metrics.views"}
        }
    }]
    agg    = list(posts_col.aggregate(pipeline))
    totals = agg[0] if agg else {}
    totals.pop("_id", None)
    return jsonify({"total_posts": total_posts, **totals})


@posts_bp.route("/<post_id>", methods=["GET"])
def get_post(post_id):
    post = posts_col.find_one({"_id": ObjectId(post_id)})
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(serialize(post))


@posts_bp.route("/", methods=["POST"])
@jwt_required()
def create_post():
    err = admin_required()
    if err: return err
    data    = request.json
    post_id = create_post_with_transaction(data)
    return jsonify({"status": "created", "post_id": post_id}), 201


@posts_bp.route("/<post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    err = admin_required()
    if err: return err
    data             = request.json
    expected_version = data.get("version")
    update_fields    = {
        "text":       data["text"],
        "version":    expected_version + 1,
        "updated_at": datetime.utcnow()
    }
    result = posts_col.update_one(
        {"_id": ObjectId(post_id), "version": expected_version},
        {"$set": update_fields}
    )
    if result.matched_count == 0:
        return jsonify({
            "status":  "conflict",
            "message": "Version mismatch — post was edited by someone else"
        }), 409
    return jsonify({"status": "updated", "new_version": expected_version + 1})


@posts_bp.route("/<post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    err = admin_required()
    if err: return err
    result = posts_col.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({"status": "deleted"})


@posts_bp.route("/<post_id>/lock", methods=["POST"])
@jwt_required()
def lock_post(post_id):
    claims = get_jwt()
    owner  = claims.get("sub")
    result = acquire_lock(post_id, owner)
    status = 200 if result["success"] else 423
    return jsonify(result), status


@posts_bp.route("/<post_id>/lock", methods=["DELETE"])
@jwt_required()
def unlock_post(post_id):
    claims = get_jwt()
    owner  = claims.get("sub")
    result = release_lock(post_id, owner)
    return jsonify(result)


@posts_bp.route("/<post_id>/lock", methods=["GET"])
def get_lock_status(post_id):
    return jsonify(check_lock(post_id))