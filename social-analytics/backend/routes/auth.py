from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from db import db
import bcrypt

auth_bp = Blueprint("auth", __name__)
users_auth_col = db["users_auth"]

# ── LOGIN ──────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_auth_col.find_one({"username": username})

    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check password
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Wrong password"}), 401

    # Create token with role inside it
    token = create_access_token(
        identity=username,
        additional_claims={"role": user["role"]}
    )

    return jsonify({
        "token": token,
        "role":  user["role"],
        "username": username
    })

# ── GET current user info ──────────────────────────────────
@auth_bp.route("/me")
@jwt_required()
def me():
    claims = get_jwt()
    return jsonify({
        "username": claims.get("sub"),
        "role":     claims.get("role")
    })