from flask import Blueprint, request, jsonify
from services.utility_service import (
    create_utility_payment_service,
    get_utility_payment_service,
    list_utility_payment_service
)

bp = Blueprint("utility", __name__, url_prefix="/api/v1/utility")


@bp.route("/", methods=["GET"])
def list_utilities():
    return jsonify(list_utility_payment_service())


@bp.route("/", methods=["POST"])
def create_utility():
    data = request.get_json()
    return jsonify(create_utility_payment_service(data))


@bp.route("/<payment_id>", methods=["GET"])
def utility_detail(payment_id):
    return jsonify(get_utility_payment_service(payment_id))
