from flask import Blueprint, request, jsonify
import decimal # <--- FIX: Thêm import này
from datetime import datetime # <--- FIX: Thêm import này

from services.transaction_service import (
    list_transactions_service,
    get_transaction_service,
    transfer_create_service,
    transfer_confirm_service,
    deposit_create_service,
    deposit_confirm_service,
    withdraw_create_service,
    withdraw_confirm_service,
    get_user_by_account_service
)

# Base URL: /api/v1/transactions
bp = Blueprint("transactions", __name__, url_prefix="/api/v1/transactions")

# =============================
# Helper: Validate input
# =============================
def require_fields(data, fields):
    if not data:
        return {"status": "error", "message": "No JSON data provided"}
    missing = [f for f in fields if f not in data]
    if missing:
        return {
            "status": "error",
            "message": f"Missing required fields: {', '.join(missing)}"
        }
    return None

# =============================
# Helper: Serialize DB Row (Fix lỗi JSON date/decimal)
# =============================
def serialize_row(row):
    """
    Chuyển đổi các object Python (Date, Decimal) thành JSON-friendly (String, Float)
    """
    if not row: return None
    new_row = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            # Chuyển ngày tháng thành chuỗi ISO 8601 (VD: "2023-12-22T09:00:00")
            new_row[key] = value.isoformat() 
        elif isinstance(value, decimal.Decimal):
            # Chuyển Decimal thành float để hiển thị trên UI
            new_row[key] = float(value)
        else:
            new_row[key] = value
    return new_row

# =============================
# 1. Lấy lịch sử giao dịch (Có phân trang)
# =============================
@bp.route('/history', methods=['GET'])
def get_history():
    account_id = request.args.get('account_id')
    page = int(request.args.get('page', 1))
    
    if not account_id:
        return jsonify({"status": "error", "message": "Missing account_id"}), 400

    # Import tại đây hoặc trên đầu đều được, nhưng tốt nhất là trên đầu nếu không bị circular import
    from services.transaction_service import get_account_transactions_service
    result = get_account_transactions_service(account_id, page=page)

    if result['status'] == 'success':
        # FIX: Áp dụng serialize cho danh sách trả về
        sanitized_data = [serialize_row(row) for row in result['data']]
        return jsonify({"status": "success", "data": sanitized_data})
    
    return jsonify(result), 400 # <--- FIX: Sửa 40 thành 400

# =============================
# 2. Lấy danh sách (Admin/Search chung)
# =============================
@bp.route("", methods=["GET"])
def list_transactions_route():
    account_id = request.args.get("account_id")
    result = list_transactions_service(account_id)
    
    if result["status"] == "success":
        # FIX: Phải serialize data ở đây nữa, nếu không sẽ crash
        sanitized_data = [serialize_row(row) for row in result['data']]
        return jsonify({"status": "success", "data": sanitized_data}), 200
        
    return jsonify(result), 400

# =============================
# 3. Lấy chi tiết 1 giao dịch
# =============================
@bp.route("/<transaction_id>", methods=["GET"])
def get_transaction_route(transaction_id):
    result = get_transaction_service(transaction_id)
    
    if result["status"] == "success":
        # FIX: Serialize single object
        sanitized_data = serialize_row(result['data'])
        return jsonify({"status": "success", "data": sanitized_data}), 200
        
    return jsonify(result), 404

# ==========================================================
#                     TRANSFER (CHUYỂN KHOẢN)
# ==========================================================

@bp.route("/transfer/create", methods=["POST"])
def transfer_create_route():
    data = request.get_json()
    print("Data received:", data)
    error = require_fields(data, ["from_account_id", "to_account_number", "amount"])
    if error: return jsonify(error), 400

    result = transfer_create_service(
        from_account_id=data["from_account_id"],
        to_account_number=data["to_account_number"],
        amount=data["amount"],
        to_bank_code=data.get("to_bank_code", "LOCAL"),
        currency=data.get("currency", "VND"),
        note=data.get("note")
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

@bp.route("/transfer/confirm", methods=["POST"])
def transfer_confirm_route():
    data = request.get_json()
    error = require_fields(data, ["transaction_id", "otp_code"])
    if error: return jsonify(error), 400

    result = transfer_confirm_service(
        transaction_id=data["transaction_id"],
        otp_code=data["otp_code"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

# ==========================================================
#                     DEPOSIT (NẠP TIỀN)
# ==========================================================

@bp.route("/deposit/create", methods=["POST"])
def deposit_create_route():
    data = request.get_json()
    error = require_fields(data, ["account_id", "amount"])
    if error: return jsonify(error), 400

    result = deposit_create_service(
        account_id=data["account_id"],
        amount=data["amount"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

@bp.route("/deposit/confirm", methods=["POST"])
def deposit_confirm_route():
    data = request.get_json() or {}
    # Hỗ trợ cả 2 key otp hoặc otp_code
    otp = data.get("otp_code") or data.get("otp")
    
    if not data.get("transaction_id") or not otp:
         return jsonify({"status": "error", "message": "Missing transaction_id or otp"}), 400

    result = deposit_confirm_service(
        transaction_id=data["transaction_id"],
        otp_code=otp
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

# ==========================================================
#                     WITHDRAW (RÚT TIỀN)
# ==========================================================

@bp.route("/withdraw/create", methods=["POST"])
def withdraw_create_route():
    data = request.get_json()
    error = require_fields(data, ["account_id", "amount"])
    if error: return jsonify(error), 400

    result = withdraw_create_service(
        account_id=data["account_id"],
        amount=data["amount"]
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

@bp.route("/withdraw/confirm", methods=["POST"])
def withdraw_confirm_route():
    data = request.get_json() or {}
    otp = data.get("otp_code") or data.get("otp")
    
    if not data.get("transaction_id") or not otp:
        return jsonify({"status": "error", "message": "Missing transaction_id or otp"}), 400

    result = withdraw_confirm_service(
        transaction_id=data["transaction_id"],
        otp_code=otp
    )
    return jsonify(result), 200 if result["status"] == "success" else 400

@bp.route('/lookup/<account_number>', methods=['GET'])
def lookup_account_route(account_number):
    # Gọi hàm service chúng ta vừa sửa ở trên
    result = get_user_by_account_service(account_number)
    
    if result:
        return jsonify({
            "status": "success",
            "full_name": result['full_name']
        }), 200
    
    return jsonify({
        "status": "error",
        "message": "Không tìm thấy tài khoản"
    }), 404