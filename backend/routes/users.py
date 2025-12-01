from flask import Blueprint, request, jsonify
from services.user_service import (
    create_user,
    get_user_detail,
    update_user_info,
    list_users
)

bp = Blueprint("users", __name__, url_prefix="/api/v1/users")

@bp.route("", methods=["POST"])
def create_user_route():
    data = request.get_json()
    result = create_user(data)
    return jsonify(result), result.get("status_code", 200)

@bp.route("/<user_id>", methods=["GET"])
def get_user_route(user_id):
    result = get_user_detail(user_id)
    return jsonify(result), result.get("status_code", 200)

@bp.route("/<user_id>", methods=["PUT"])
def update_user_route(user_id):
    data = request.get_json()
    result = update_user_info(user_id, data)
    return jsonify(result), result.get("status_code", 200)

@bp.route("", methods=["GET"])
def list_users_route():
    keyword = request.args.get("keyword", "")
    result = list_users(keyword)
    return jsonify(result), 200
