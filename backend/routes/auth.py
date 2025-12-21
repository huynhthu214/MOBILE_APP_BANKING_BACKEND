from flask import Blueprint, request, jsonify
from services.auth_service import (
    login,
    logout,
    refresh,
    forgot_password,
    reset_password,
    change_password
)

from services.user_service import get_me
from services.security_utils import decode_access_token

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@bp.route('/login', methods=['POST'])
def login_route():
    data = request.get_json()
    result = login(data)
    return jsonify(result), result.get("status_code", 200)


@bp.route('/logout', methods=['POST'])
def logout_route():
    data = request.get_json() or {}
    auth_header = request.headers.get('Authorization')
    result = logout(data, auth_header)
    return jsonify(result), result.get("status_code", 200)


@bp.route('/refresh', methods=['POST'])
def refresh_route():
    data = request.get_json() or {}
    result = refresh(data)
    return jsonify(result), result.get("status_code", 200)

@bp.route('/me', methods=['GET'])
def me_route():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            "status": "error",
            "message": "Missing access token"
        }), 401

    token = auth_header.split(' ')[1]

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

@bp.route('/forgot-password', methods=['POST'])
def forgot_password_route():
    data = request.get_json()
    result = forgot_password(data)
    return jsonify(result), result.get("status_code", 200)


@bp.route('/reset-password', methods=['POST'])
def reset_password_route():
    data = request.get_json()
    result = reset_password(data)
    return jsonify(result), result.get("status_code", 200)

@bp.route("/change-password", methods=["POST"])
def change_password_route():
    # 1. Lấy token từ Header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"status": "error", "message": "Missing token"}), 401
    
    token = auth_header.replace("Bearer ", "")
    payload, err = decode_access_token(token)
    if err:
        return jsonify({"status": "error", "message": err}), 401
    
    user_id = payload.get("sub") 
    data = request.get_json()
    result = change_password(user_id, data) 
    
    return jsonify(result), result.get("status_code", 200)