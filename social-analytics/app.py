import sys
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv  # <-- Make sure this line is here!

# Import your blueprints
from routes.dashboard import dashboard_bp
from routes.posts     import posts_bp
from routes.hashtags  import hashtags_bp
from routes.search    import search_bp
from routes.auth      import auth_bp
from routes.users     import users_bp
from routes.reports   import reports_bp

load_dotenv()

app = Flask(__name__)
CORS(app)
# ... (the rest of your app.py code remains exactly the same)

# JWT Manager configuration
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "supersecret_social_analytics_2024"
)
jwt = JWTManager(app)

# Register your foundational blueprints
app.register_blueprint(auth_bp,      url_prefix="/api/auth")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(posts_bp,     url_prefix="/api/posts")
app.register_blueprint(hashtags_bp,  url_prefix="/api/hashtags")
app.register_blueprint(search_bp,    url_prefix="/api/search")
app.register_blueprint(users_bp,     url_prefix="/api/users")

# Register the new reports blueprint to cleanly process Chart.js endpoint requests
app.register_blueprint(reports_bp,   url_prefix="/api/reports")

@app.route("/")
def home():
    return {"status": "Social Analytics API running", "version": "1.0"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)