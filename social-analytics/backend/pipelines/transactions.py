from db import db, posts_col, user_metrics_col
import datetime

def create_post_with_transaction(post_data):
    """
    Creates a post AND updates user metrics atomically.
    If either operation fails, both are rolled back.
    This demonstrates ACID transactions in MongoDB.
    """
    client = db.client

    with client.start_session() as session:
        with session.start_transaction():
            # Step 1 — Insert the post
            post_doc = {
                "text":       post_data["text"],
                "username":   post_data["username"],
                "user_id":    post_data.get("user_id", "u_manual"),
                "platform":   post_data.get("platform", "Twitter/X"),
                "post_type":  post_data.get("post_type", "text"),
                "hashtags":   [t.strip("#") for t in post_data["text"].split() if t.startswith("#")],
                "created_at": datetime.datetime.utcnow(),
                "metrics":    {"likes": 0, "retweets": 0, "replies": 0, "views": 0},
                "sentiment":  {"label": "neutral", "score": 0.5},
                "lang":       "en",
                "version":    1
            }

            result = posts_col.insert_one(post_doc, session=session)
            post_id = result.inserted_id

            # Step 2 — Update user metrics atomically
            user_metrics_col.update_one(
                {"username": post_data["username"]},
                {
                    "$inc":  {"total_posts": 1},
                    "$set":  {"last_post_at": datetime.datetime.utcnow()},
                    "$setOnInsert": {"username": post_data["username"]}
                },
                upsert=True,
                session=session
            )

    return str(post_id)
