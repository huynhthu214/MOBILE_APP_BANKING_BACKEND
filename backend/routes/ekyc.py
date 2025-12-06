from flask import Blueprint, request, jsonify
from services.ekyc_service import create_ekyc, get_ekyc, review_ekyc, get_pending_list, update_ekyc, get_ekyc_detail_by_id

bp = Blueprint("ekyc", __name__, url_prefix="/api/v1/users")

@bp.route("/pending", methods=["GET"])
def get_pending():
    result = get_pending_list()
    return jsonify(result), result["status_code"]

@bp.route("/<user_id>/ekyc", methods=["PATCH"])
def update_ekyc_route(user_id):
    data = request.get_json()
    result = update_ekyc(user_id, data)
    return jsonify(result), result.get("status_code", 200)

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

@bp.route("/ekyc/<ekyc_id>", methods=["GET"])
def get_ekyc_by_id_route(ekyc_id):
    result = get_ekyc_detail_by_id(ekyc_id)
    return jsonify(result), result["status_code"]