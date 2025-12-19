from flask import Blueprint, request, jsonify
from services.otp_service import create_otp, verify_otp_util

bp = Blueprint("otp", __name__, url_prefix="/api/v1/otp")

@bp.route("/send", methods=["POST"])
def send():
    data = request.json
    user_id = data.get("USER_ID")
    purpose = data.get("PURPOSE", "transaction")

    if not user_id:
        return jsonify({"status":"error","message":"USER_ID required"}), 400

    otp_id, code = create_otp(user_id, purpose)

    return jsonify({
        "status": "success",
        "data": {
            "otp_id": otp_id,
            "otp_code_dev": code
        }
    })


@bp.route("/verify", methods=["POST"])
def verify():
    data = request.json

    user_id = data.get("user_id")
    otp_code = data.get("otp_code")
    purpose = data.get("purpose", "forgot_password")

    if not user_id or not otp_code:
        return jsonify({
            "status": "error",
            "message": "Missing fields"
        }), 400

    ok, msg = verify_otp_util(user_id, otp_code, purpose)

    if not ok:
        return jsonify({
            "status": "error",
            "message": msg
        }), 400

    return jsonify({
        "status": "success",
        "message": msg
    })

@bp.route("", methods=["GET"])
def list_all():
    return jsonify({"status":"success","data": list_otps()})
