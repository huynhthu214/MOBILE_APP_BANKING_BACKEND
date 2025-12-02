# routes/payments.py
from flask import Blueprint, request, jsonify
from services.payment_service import (
    list_bills_service,
    get_bill_service,
    pay_bill_service,
    create_utility_payment_service
)

bp = Blueprint("payments", __name__, url_prefix="/api/v1/payments")

# =============================
# Lấy danh sách hóa đơn
# =============================
@bp.route("/bills", methods=["GET"])
def list_bills_route():
    keyword = request.args.get("keyword", "")
    result = list_bills_service(keyword)
    return jsonify(result), 200 if result.get("status") == "success" else 400

# =============================
# Lấy chi tiết hóa đơn
# =============================
@bp.route("/bills/<bill_id>", methods=["GET"])
def get_bill_route(bill_id):
    result = get_bill_service(bill_id)
    return jsonify(result), result.get("status_code", 200)

# =============================
# Thanh toán hóa đơn
# =============================
@bp.route("/bills/pay", methods=["POST"])
def pay_bill_route():
    data = request.get_json()
    if not data or "account_id" not in data or "bill_id" not in data:
        return jsonify({"status": "error", "message": "account_id and bill_id are required"}), 400

    account_id = data.get("account_id")
    bill_id = data.get("bill_id")
    result = pay_bill_service(account_id, bill_id)
    return jsonify(result), 200 if result.get("status") == "success" else 400

# =============================
# Tạo thanh toán dịch vụ tiện ích
# =============================
@bp.route("/utility-payments", methods=["POST"])
def create_utility_payment_route():
    data = request.get_json()
    required_fields = ["transaction_id", "provider_code", "reference_code_1", "reference_code_2"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": f"Missing required fields: {', '.join(required_fields)}"}), 400

    transaction_id = data.get("transaction_id")
    provider_code = data.get("provider_code")
    ref1 = data.get("reference_code_1")
    ref2 = data.get("reference_code_2")

    result = create_utility_payment_service(transaction_id, provider_code, ref1, ref2)
    return jsonify(result), 200 if result.get("status") == "success" else 400
