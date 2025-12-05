from flask import Blueprint, request, jsonify
from services.account_service import (
    create_account, list_accounts, get_account, update_account,
    create_saving_detail, get_saving_detail,
    create_mortage_detail, get_mortage_detail,
    get_account_summary
)

bp = Blueprint("account", __name__, url_prefix="/api/v1/accounts")

# ===== ACCOUNT =====
@bp.route("", methods=["POST"])
def route_create_account():
    data = request.json
    return jsonify(create_account(**data))

@bp.route("", methods=["GET"])
def route_list_accounts():
    return jsonify(list_accounts())

@bp.route("/<account_id>", methods=["GET"])
def route_get_account(account_id):
    return jsonify(get_account(account_id))

@bp.route("/<account_id>", methods=["PUT"])
def route_update_account(account_id):
    data = request.json
    return jsonify(update_account(account_id, **data))

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

# ===== MORTAGE DETAIL =====
@bp.route("/<account_id>/mortage-detail", methods=["POST"])
def route_create_mortage_detail(account_id):
    data = request.json
    return jsonify(create_mortage_detail(account_id, **data))

@bp.route("/<account_id>/mortage-detail", methods=["GET"])
def route_get_mortage_detail(account_id):
    return jsonify(get_mortage_detail(account_id))
