from flask import Blueprint, request, jsonify
from services.otp_service import send_otp, verify_otp, list_otps

bp = Blueprint("otp", __name__, url_prefix="/api/v1")

@bp.route("/auth/send-otp", methods=["POST"])
def route_send_otp():
    data = request.json
    return jsonify(send_otp(data.get("USER_ID"), data.get("PURPOSE", "transaction")))

@bp.route("/auth/verify-otp", methods=["POST"])
def route_verify_otp():
    data = request.json
    return jsonify(verify_otp(data.get("USER_ID"), data.get("CODE"), data.get("PURPOSE", "transaction")))

@bp.route("/otp", methods=["GET"])
def route_list_otps():
    return jsonify(list_otps())
