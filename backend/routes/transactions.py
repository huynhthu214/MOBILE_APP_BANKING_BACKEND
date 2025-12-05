from flask import Blueprint, request, jsonify
from services.transaction_service import (
    get_transaction_service,
    list_transactions_service,
    transfer_create_service,
    transfer_confirm_service,
    deposit_service,
    withdraw_service,
    deposit_create_service,
    deposit_confirm_service,
    withdraw_create_service,
    withdraw_confirm_service
)

bp = Blueprint("transactions", __name__, url_prefix="/api/v1/transactions")

@bp.route("/deposit", methods=["POST"])
def deposit_create_route():
    data = request.get_json()
    result = deposit_create_service(
        data["account_id"],
        data["amount"]
    )
    return jsonify(result)

@bp.route("/deposit/confirm", methods=["POST"])
def deposit_confirm_route():
    data = request.get_json()
    result = deposit_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result)

@bp.route("/withdraw", methods=["POST"])
def withdraw_create_route():
    data = request.get_json()
    result = withdraw_create_service(
        data["account_id"],
        data["amount"]
    )
    return jsonify(result)

@bp.route("/withdraw/confirm", methods=["POST"])
def withdraw_confirm_route():
    data = request.get_json()
    result = withdraw_confirm_service(
        data["transaction_id"],
        data["otp"]
    )
    return jsonify(result)

# Helper: validate input
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

    return jsonify(result), 200 if result.get("status") == "success" else 400


# =============================
# Lấy chi tiết giao dịch
# =============================
@bp.route("/<transaction_id>", methods=["GET"])
def get_transaction_route(transaction_id):
    result = get_transaction_service(transaction_id)
    return jsonify(result), result.get("status_code", 200)


# =============================
# Khởi tạo giao dịch chuyển khoản (step 1 → tạo + gửi OTP)
# =============================
@bp.route("/transfer", methods=["POST"])
def transfer_route():
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

    return jsonify(result), 200 if result.get("status") == "success" else 400


# =============================
# Xác nhận giao dịch bằng OTP (step 2)
# =============================
@bp.route("/confirm", methods=["POST"])
def confirm_transaction_route():
    data = request.get_json() or {}

    required = ["transaction_id", "otp"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = transfer_confirm_service(
        data["transaction_id"],
        data["otp"]
    )

    return jsonify(result), 200 if result.get("status") == "success" else 400


# =============================
# Nạp tiền
# =============================
@bp.route("/deposit", methods=["POST"])
def deposit_route():
    data = request.get_json() or {}

    required = ["account_id", "amount"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = deposit_service(
        data["account_id"],
        data["amount"]
    )

    return jsonify(result), 200 if result.get("status") == "success" else 400


# =============================
# Rút tiền
# =============================
@bp.route("/withdraw", methods=["POST"])
def withdraw_route():
    data = request.get_json() or {}

    required = ["account_id", "amount"]
    check = require_fields(data, required)
    if check:
        return jsonify(check), 400

    result = withdraw_service(
        data["account_id"],
        data["amount"]
    )

    return jsonify(result), 200 if result.get("status") == "success" else 400
