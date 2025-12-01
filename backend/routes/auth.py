from flask import Blueprint, request, jsonify
from services.auth_service import (
    login,
    logout,
    refresh,
    send_otp,
    verify_otp
)

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


@bp.route('/send-otp', methods=['POST'])
def send_otp_route():
    data = request.get_json() or {}
    result = send_otp(data)
    return jsonify(result), result.get("status_code", 200)


@bp.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json() or {}
    result = verify_otp(data)
    return jsonify(result), result.get("status_code", 200)

