from flask import Blueprint, request, jsonify
from services.utility_service import (
    utility_topup_create_service,
    utility_topup_confirm_service,
    get_utility_payment_service
)

bp = Blueprint("utility", __name__, url_prefix="/api/v1/utility")


# =============================
# Helper: validate input
# =============================
def require_fields(data, fields):
    missing = [f for f in fields if f not in data]
    if missing:
        return {
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing)}"
        }
    return None


# =====================================================
# Step 1 – Create utility payment + send OTP
# POST /api/v1/utility/topup
# =====================================================
@bp.route("/topup", methods=["POST"])
def utility_topup_create_route():
    data = request.get_json() or {}
    required = ["account_id", "provider", "phone_number", "amount"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = utility_topup_create_service(
        data["account_id"],
        data["provider"],
        data["phone_number"],
        data["amount"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# =====================================================
# Step 2 – Confirm utility payment by OTP
# POST /api/v1/utility/confirm
# =====================================================
@bp.route("/confirm", methods=["POST"])
def utility_topup_confirm_route():
    data = request.get_json() or {}
    required = ["transaction_id", "otp"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = utility_topup_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# =====================================================
# Get utility payment detail
# GET /api/v1/utility/<UTILITY_PAYMENT_ID>
# =====================================================
@bp.route("/<utility_payment_id>", methods=["GET"])
def utility_detail_route(utility_payment_id):
    result = get_utility_payment_service(utility_payment_id)
    return jsonify(result), 200 if result["status"] == "success" else 404
