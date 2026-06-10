from flask import Blueprint, jsonify
# Import from your central db config to reuse the connection pool safely
from db import posts_col, users_col 

reports_bp = Blueprint('reports', __name__)

# ── 1. KPI COUNTERS ───────────────────────────────────────────────────
@reports_bp.route('/kpis', methods=['GET'])
def get_kpis():
    try:
        total_posts = posts_col.count_documents({})
        total_users = users_col.count_documents({})

        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "totalLikes": {"$sum": "$metrics.likes"},
                    "totalViews": {"$sum": "$metrics.views"}
                }
            }
        ]
        agg = list(posts_col.aggregate(pipeline))
        # Pull the first dictionary item out of the list safely
        metrics = agg[0] if agg else {"totalLikes": 0, "totalViews": 0}

        return jsonify({
            "totalPosts": total_posts,
            "totalUsers": total_users,
            "totalLikes": metrics.get("totalLikes", 0),
            "totalViews": metrics.get("totalViews", 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── 2. PLATFORM SUMMARY MATRIX ────────────────────────────────────────
@reports_bp.route('/platform-summary', methods=['GET'])
def get_platform_summary():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$platform",
                    "count": {"$sum": 1},
                    "totalLikes": {"$sum": "$metrics.likes"},
                    "avgLikes": {"$avg": "$metrics.likes"},
                    "totalReplies": {"$sum": "$metrics.replies"},
                    "totalRetweets": {"$sum": "$metrics.retweets"},
                    "totalViews": {"$sum": "$metrics.views"}
                }
            }
        ]
        return jsonify(list(posts_col.aggregate(pipeline)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── 3. TOP HASHTAGS PIPELINE ──────────────────────────────────────────
@reports_bp.route('/hashtags', methods=['GET'])
def get_top_hashtags():
    try:
        pipeline = [
            {"$unwind": "$hashtags"},
            {"$group": {"_id": "$hashtags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        return jsonify(list(posts_col.aggregate(pipeline)))
    except Exception as e:
        return jsonify({"error": str(e)}), 500