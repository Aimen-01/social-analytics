from flask import Blueprint, jsonify, request
from db import posts_col

search_bp = Blueprint("search", __name__)

@search_bp.route("/")
def search():
    # 1. Capture parameters matching search.html request fields
    query_text  = request.args.get("q", "").strip()
    platform    = request.args.get("platform", "").strip()
    post_type   = request.args.get("post_type", "").strip() # Maps to your format filter
    sentiment   = request.args.get("sentiment", "").strip()
    
    sort_column = request.args.get("sort", "created_at")
    direction   = request.args.get("direction", "desc")
    limit       = int(request.args.get("limit", 50))

    # 2. Dynamically build the MongoDB find query criteria
    query = {}

    if query_text:
        query["text"] = {"$regex": query_text, "$options": "i"}
    if platform:
        query["platform"] = platform
    if post_type:
        query["post_type"] = post_type
    if sentiment:
        query["sentiment.label"] = sentiment

    # 3. Determine MongoDB Sorting Order (1 for ASC, -1 for DESC)
    sort_order = -1 if direction == "desc" else 1

    try:
        # 4. Fetch documents using the dynamic criteria and sorting parameters
        posts = list(posts_col.find(query)
                     .sort(sort_column, sort_order)
                     .limit(limit))

        # 5. Serialize MongoDB ObjectId values cleanly into JSON-safe strings
        for p in posts:
            p["_id"] = str(p["_id"])

        # FIX: Return a direct flat array list straight to search.html's fetch parser
        return jsonify(posts)

    except Exception as e:
        return jsonify({"error": str(e)}), 500