from flask import Blueprint, request, jsonify
from services.account_service import (
    create_account, list_accounts, get_account, update_account,
    create_saving_detail, get_saving_detail,
    create_mortage_detail, get_mortage_detail,
    update_saving_interest,
    close_saving,
    pay_mortgage,
    get_account_summary,
    update_global_rates,
    get_rates_from_file,
    get_account_detail.
    get_rates_from_file
    # ĐÃ XÓA: get_account_detail_service (vì hàm này đã gộp vào get_account_summary)
)

bp = Blueprint("account", __name__, url_prefix="/api/v1/accounts")

@bp.route("/rates", methods=["GET", "PUT"])
def route_handle_rates():
    if request.method == "GET":
        current_rates = get_rates_from_file()
        return jsonify({"status": "success", "data": current_rates})

    if request.method == "PUT":
        data = request.json
        return jsonify(update_global_rates(data))

# ===== ACCOUNT =====
@bp.route("", methods=["POST"])
def route_create_account():
    data = request.json
    return jsonify(create_account(**data))

@bp.route("", methods=["GET"])
def route_list_accounts():
    # Lấy tham số 'search' từ URL: /api/v1/accounts?search=123
    search_query = request.args.get('search', None)
    result = list_accounts(search_query)
    return jsonify(result), 200

@bp.route("/<account_id>", methods=["GET"])
def route_get_account(account_id):
    result = get_account_detail(account_id)
    status_code = 200 if result["status"] == "success" else 404
    return jsonify(result), status_code

@bp.route("/<account_id>", methods=["PUT"])
def route_update_account(account_id):
    data = request.json
    if 'rate_12m' in data:
        del data['rate_12m']
        
    return jsonify(update_account(account_id, **data))

# --- ĐÂY LÀ ROUTE CHUẨN ĐỂ LẤY CHI TIẾT TÀI KHOẢN ---
@bp.route("/<account_id>/summary", methods=["GET"])
def route_account_summary(account_id):
    result = get_account_summary(account_id)
    return jsonify(result), 200 if result["status"] == "success" else 400

# ===== SAVING DETAIL =====
@bp.route("/<account_id>/saving-detail", methods=["POST"])
def route_create_saving_detail(account_id):
    data = request.json
    return jsonify(create_saving_detail(account_id, **data))

@bp.route("/<account_id>/saving-detail", methods=["GET"])
def route_get_saving_detail(account_id):
    return jsonify(get_saving_detail(account_id))

@bp.route("/saving/<account_id>/profit", methods=["GET"])
def route_get_saving_profit(account_id):
    from services.account_service import get_saving_profit
    return jsonify(get_saving_profit(account_id))

# ===== UPDATE SAVING INTEREST =====
@bp.route("/<account_id>/saving/interest", methods=["PUT"])
def route_update_saving_interest(account_id):
    data = request.json
    new_rate = data.get("interest_rate")
    if new_rate is None:
        return jsonify({"status":"error","message":"Missing interest_rate"}), 400
    return jsonify(update_saving_interest(account_id, new_rate))

@bp.route("/<account_id>/saving/close", methods=["POST"])
def route_close_saving(account_id):
    return jsonify(close_saving(account_id))

# ===== MORTAGE DETAIL =====
@bp.route("/<account_id>/mortage-detail", methods=["POST"])
def route_create_mortage_detail(account_id):
    data = request.json
    return jsonify(create_mortage_detail(account_id, **data))

@bp.route("/<account_id>/mortage-detail", methods=["GET"])
def route_get_mortage_detail(account_id):
    return jsonify(get_mortage_detail(account_id))

@bp.route("/<account_id>/mortgage/pay", methods=["POST"])
def route_pay_mortgage(account_id):
    data = request.json
    amount = data.get("amount")
    if amount is None:
        return jsonify({"status":"error","message":"Missing amount"}), 400
    return jsonify(pay_mortgage(account_id, amount))

@bp.route("/mortgage/<account_id>/schedule", methods=["GET"])
def route_get_mortgage_schedule(account_id):
    from services.account_service import get_mortgage_schedule
    return jsonify(get_mortgage_schedule(account_id))

