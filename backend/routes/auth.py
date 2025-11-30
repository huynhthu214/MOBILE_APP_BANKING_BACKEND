from flask import Blueprint, request, jsonify
from database.db import get_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({
            "status": "success",
            "user_id": user["id"],
            "role": user["role"]
        })
    else:
        return jsonify({"status": "fail"}), 401
