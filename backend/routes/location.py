from flask import Blueprint, request, jsonify
from services.location_service import (
    create_branch,
    get_all_branches,
    get_branch_by_id_service,
    update_branch,
    delete_branch,
    find_nearby_branches,
    calculate_simple_route
)

bp = Blueprint("location", __name__, url_prefix="/api/v1/branches")


# ============================
# GET NEARBY
# ============================
@bp.route("/nearby", methods=["GET"])
def nearby():
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
        radius_m = float(request.args.get("radius_m"))
    except:
        return jsonify({"message": "lat, lng, radius_m phải là số"}), 400

    result = find_nearby_branches(lat, lng, radius_m)

    return jsonify({
        "message": "success",
        "count": len(result),
        "data": result
    })


# ============================
# GET ROUTE
# ============================
@bp.route("/<branch_id>/route", methods=["GET"])
def route_to_branch(branch_id):
    try:
        from_lat = float(request.args.get("from_lat"))
        from_lng = float(request.args.get("from_lng"))
    except:
        return jsonify({"message": "from_lat/from_lng phải là số"}), 400

    result = calculate_simple_route(branch_id, from_lat, from_lng)

    if not result:
        return jsonify({"message": "Branch not found"}), 404

    return jsonify({
        "message": "success",
        "data": result
    })


# ============================
# POST
# ============================
@bp.route("", methods=["POST"])
def create():
    data = request.json
    return jsonify(create_branch(data))


# ============================
# GET ALL
# ============================
@bp.route("", methods=["GET"])
def get_all():
    return jsonify({
        "message": "success",
        "data": get_all_branches()
    })


# ============================
# GET ONE
# ============================
@bp.route("/<branch_id>", methods=["GET"])
def get_one(branch_id):
    result = get_branch_by_id_service(branch_id)

    if not result:
        return jsonify({"message": "not_found"}), 404

    return jsonify({
        "message": "success",
        "data": result
    })


# ============================
# PUT
# ============================
@bp.route("/<branch_id>", methods=["PUT"])
def update(branch_id):
    data = request.json
    return jsonify(update_branch(branch_id, data))


# ============================
# DELETE
# ============================
@bp.route("/<branch_id>", methods=["DELETE"])
def delete(branch_id):
    return jsonify(delete_branch(branch_id))
