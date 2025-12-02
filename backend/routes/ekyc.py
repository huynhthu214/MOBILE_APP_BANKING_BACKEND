from flask import Blueprint, request, jsonify
from services.ekyc_service import create_ekyc, get_ekyc, review_ekyc

bp = Blueprint("ekyc", __name__, url_prefix="/api/v1/users")

@bp.route("/<user_id>/ekyc", methods=["POST"])
def create_ekyc_route(user_id):
    data = request.get_json()
    result = create_ekyc(user_id, data)
    return jsonify(result), result.get("status_code", 200)


@bp.route("/<user_id>/ekyc", methods=["GET"])
def get_ekyc_route(user_id):
    result = get_ekyc(user_id)
    return jsonify(result), result.get("status_code", 200)


@bp.route("/<user_id>/ekyc/review", methods=["PUT"])
def review_ekyc_route(user_id):
    data = request.get_json()
    result = review_ekyc(user_id, data)
    return jsonify(result), result.get("status_code", 200)
