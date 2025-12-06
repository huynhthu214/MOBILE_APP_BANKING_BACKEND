from flask import Blueprint, request, jsonify
import jwt
from config import JWT_SECRET, JWT_ALGORITHM
from services.auth_service import (
    login,
    logout,
    refresh,
    change_password,
    forgot_password,
    reset_password
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

@bp.route('/change-password', methods=['POST'])
def change_password_route():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"status":"error","message":"Missing access token"}), 401

    token = auth_header.split(' ')[1]

    # Decode token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('type') != 'access':
            return jsonify({"status":"error","message":"Invalid token type"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"status":"error","message":"Token expired"}), 401
    except Exception as e:
        return jsonify({"status":"error","message":"Invalid token"}), 401

    user_id = payload.get("sub")
    data = request.get_json()
    result = change_password(user_id, data)
    return jsonify(result), result.get("status_code", 200)


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