from flask import Blueprint, request, jsonify
from services.account_service import update_saving_interest

bp_admin = Blueprint("admin", __name__, url_prefix="/api/admin")

@bp_admin.route("/saving/<account_id>/profit-rate", methods=["PUT"])
def route_admin_update_profit_rate(account_id):
    data = request.json
    rate = data.get("profit_rate")

    if rate is None:
        return jsonify({"status":"error","message":"Missing profit_rate"}), 400

    return jsonify(update_saving_interest(account_id, rate))
