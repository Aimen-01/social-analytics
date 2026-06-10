from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
from pipelines.users import compute_user_metrics, get_top_users
from db import user_metrics_col

users_bp = Blueprint("users", __name__)


def serialize(doc):
    doc.pop("_id", None)
    for key in ["latest_post", "computed_at"]:
        if key in doc and hasattr(doc[key], "isoformat"):
            doc[key] = doc[key].isoformat()
    for key in ["engagement_rate", "viral_coefficient", "influence_score",
                "avg_likes", "avg_retweets"]:
        if key in doc:
            doc[key] = round(float(doc[key]), 4)
    return doc


@users_bp.route("/leaderboard")
def leaderboard():
    """
    GET /api/users/leaderboard?limit=10
    Reads pre-computed influence rankings.
    Triggers recompute if data is stale (> 30 min).
    """
    limit  = int(request.args.get("limit", 10))
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    fresh  = user_metrics_col.count_documents({"computed_at": {"$gte": cutoff}})

    if fresh == 0:
        compute_user_metrics(limit=100)

    results = get_top_users(limit=limit)
    return jsonify({"data": [serialize(r) for r in results]})


@users_bp.route("/<user_id>")
def user_detail(user_id):
    """
    GET /api/users/<user_id>
    Returns metrics for a single user.
    """
    doc = user_metrics_col.find_one({"user_id": user_id}, {"_id": 0})
    if not doc:
        return jsonify({"error": "User not found"}), 404
    return jsonify(serialize(doc))


@users_bp.route("/refresh", methods=["POST"])
@jwt_required()
def refresh():
    """
    POST /api/users/refresh
    Manually triggers pipeline recompute. Admin only.
    """
    results = compute_user_metrics(limit=100)
    return jsonify({"recomputed": len(results)})