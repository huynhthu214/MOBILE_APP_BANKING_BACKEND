from flask import Blueprint, jsonify
from services.system_service import seed_system

bp = Blueprint("system", __name__, url_prefix="/api/v1/system")

@bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": "ok",
        "message": "Server is running"
    })

@bp.route("/seed", methods=["POST"])
def seed():
    return seed_system()