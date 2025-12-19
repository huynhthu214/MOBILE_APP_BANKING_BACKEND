from flask import Blueprint, request, jsonify
from services.transaction_service import (
    list_transactions_service,
    get_transaction_service,
    transfer_create_service,
    transfer_confirm_service,
    deposit_create_service,
    deposit_confirm_service,
    withdraw_create_service,
    withdraw_confirm_service
)

bp = Blueprint("transactions", __name__, url_prefix="/api/v1/transactions")


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


# =============================
# Lấy danh sách giao dịch
# =============================
@bp.route("", methods=["GET"])
def list_transactions_route():
    account_id = request.args.get("account_id")
    result = list_transactions_service(account_id)
    return jsonify(result), 200 if result["status"] == "success" else 400


# =============================
# Lấy chi tiết giao dịch
# =============================
@bp.route("/<transaction_id>", methods=["GET"])
def get_transaction_route(transaction_id):
    result = get_transaction_service(transaction_id)
    return jsonify(result), result.get("status_code", 200)


# ==========================================================
#                     TRANSFER (2 bước)
# ==========================================================

# Step 1 – Create transfer + gửi OTP
@bp.route("/transfer/create", methods=["POST"])
def transfer_create_route():
    data = request.get_json() or {}
    required = ["from_account_id", "to_account_number", "amount"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = transfer_create_service(
        data["from_account_id"],
        data["to_account_number"],
        data["amount"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# Step 2 – Confirm transfer bằng OTP
@bp.route("/transfer/confirm", methods=["POST"])
def transfer_confirm_route():
    data = request.get_json() or {}
    required = ["transaction_id", "otp"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = transfer_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# ==========================================================
#                    DEPOSIT (2 bước)
# ==========================================================

# Step 1 – Tạo giao dịch nạp tiền → gửi OTP
@bp.route("/deposit/create", methods=["POST"])
def deposit_create_route():
    data = request.get_json() or {}
    required = ["account_id", "amount"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = deposit_create_service(
        data["account_id"],
        data["amount"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# Step 2 – Xác nhận OTP để hoàn tất nạp tiền
@bp.route("/deposit/confirm", methods=["POST"])
def deposit_confirm_route():
    data = request.get_json() or {}
    required = ["transaction_id", "otp"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = deposit_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# ==========================================================
#                    WITHDRAW (2 bước)
# ==========================================================

# Step 1 – Tạo giao dịch rút tiền → gửi OTP
@bp.route("/withdraw/create", methods=["POST"])
def withdraw_create_route():
    data = request.get_json() or {}
    required = ["account_id", "amount"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = withdraw_create_service(
        data["account_id"],
        data["amount"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400


# Step 2 – Xác nhận OTP để hoàn tất rút tiền
@bp.route("/withdraw/confirm", methods=["POST"])
def withdraw_confirm_route():
    data = request.get_json() or {}
    required = ["transaction_id", "otp"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = withdraw_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

