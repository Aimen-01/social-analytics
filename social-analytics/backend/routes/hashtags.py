from flask import Blueprint, jsonify, request
from pipelines.trending import get_trending_cached, compute_trending
from db import hashtags_col

hashtags_bp = Blueprint("hashtags", __name__)


@hashtags_bp.route("/trending")
def trending():
    """
    GET /api/hashtags/trending?window=24h&limit=20
    Returns trending hashtags with trend scores.
    Reads from cache if fresh, else runs pipeline.
    """
    window = request.args.get("window", "24h")
    limit  = int(request.args.get("limit", 20))
    result = get_trending_cached(window=window, limit=limit)
    result["window"] = window
    return jsonify(result)


@hashtags_bp.route("/search")
def search():
    """
    GET /api/hashtags/search?q=tech&limit=10
    Prefix search on hashtag_stats collection.
    """
    q     = request.args.get("q", "").lower().strip()
    limit = int(request.args.get("limit", 10))

    if not q:
        return jsonify({"data": []})

    results = list(
        hashtags_col.find(
            {"hashtag": {"$regex": f"^{q}"}},
            {"_id": 0}
        ).limit(limit)
    )
    return jsonify({"data": results})