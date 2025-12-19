from flask import Blueprint, request, jsonify
from services.bill_service import (
    create_bill_service,
    get_bill_service,
    list_bills_service,
    bill_pay_create_service,
    bill_pay_confirm_service
)

bp = Blueprint("bills", __name__, url_prefix="/api/v1/bills")


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
# CREATE BILL
# POST /api/v1/bills
# =====================================================
@bp.route("", methods=["POST"])
def create_bill_route():
    data = request.get_json() or {}
    required = ["user_id", "bill_type", "amount", "due_date"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = create_bill_service(
        data["user_id"],
        data["bill_type"],
        data["amount"],
        data["due_date"],
        data.get("reference_code")
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# =====================================================
# GET BILL DETAIL
# GET /api/v1/bills/<BILL_ID>
# =====================================================
@bp.route("/<bill_id>", methods=["GET"])
def get_bill_route(bill_id):
    result = get_bill_service(bill_id)
    return jsonify(result), 200 if result["status"] == "success" else 404


# =====================================================
# LIST BILLS
# GET /api/v1/bills
# =====================================================
@bp.route("", methods=["GET"])
def list_bills_route():
    user_id = request.args.get("user_id")
    result = list_bills_service(user_id)
    return jsonify(result), 200


# =====================================================
# PAY BILL – STEP 1 (create transaction + send OTP)
# POST /api/v1/bills/<BILL_ID>/pay
# =====================================================
@bp.route("/<bill_id>/pay", methods=["POST"])
def bill_pay_create_route(bill_id):
    data = request.get_json() or {}
    required = ["account_id"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = bill_pay_create_service(
        bill_id,
        data["account_id"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# =====================================================
# PAY BILL – STEP 2 (confirm OTP)
# POST /api/v1/bills/confirm
# =====================================================
@bp.route("/confirm", methods=["POST"])
def bill_pay_confirm_route():
    data = request.get_json() or {}
    required = ["transaction_id", "otp"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = bill_pay_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400