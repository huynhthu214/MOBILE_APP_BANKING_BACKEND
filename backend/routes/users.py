from flask import Blueprint, request, jsonify
from services.user_service import (
    create_user,
    get_user_detail,
    update_user_info,
    list_users, 
    search_users,
    create_customer_service,
)
from services.user_service import get_me
from services.security_utils import decode_access_token

bp = Blueprint("users", __name__, url_prefix="/api/v1/users")
admin_bp = Blueprint("admin_create_user", __name__, url_prefix="/api/v1/admin/users")
@admin_bp.route("/create", methods=["POST"])
def create_customer_route():
    data = request.get_json()
    
    # Đảm bảo gọi đúng tên hàm đã sửa ở trên
    result = create_customer_service(data) 
    
    status_code = result.get("status_code", 200)
    return jsonify(result), status_code

@bp.route("", methods=["POST"])
def create_user_route():
    data = request.get_json()
    result = create_user(data)
    return jsonify(result), result.get("status_code", 200)

@bp.route("/me", methods=["GET"])
def me_route():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({
            "status": "error",
            "message": "Missing access token"
        }), 401

    token = auth_header.replace("Bearer ", "")

    payload, err = decode_access_token(token)
    if err:
        return jsonify({
            "status": "error",
            "message": err
        }), 401

    user_id = payload.get("sub")

    data, err = get_me(user_id)
    if err:
        return jsonify({
            "status": "error",
            "message": err
        }), 404

    return jsonify({
        "status": "success",
        "data": data
    })

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

@bp.route("/search", methods=["GET"])
def route_search_users():
    keyword = request.args.get("q", "")
    return jsonify(search_users(keyword))

