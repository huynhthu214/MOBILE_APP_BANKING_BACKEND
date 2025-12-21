from flask import Blueprint, request, jsonify
from services.location_service import (
    create_branch,
    get_all_branches,
    get_branch_by_id_service,
    update_branch,
    delete_branch,
    find_nearby_branches,
    calculate_simple_route,
    geocode_address
)

bp = Blueprint("location", __name__, url_prefix="/api/v1/branches")

@bp.route("/geocode", methods=["GET"])
def get_coords_from_address():
    address = request.args.get("address")
    if not address:
        return jsonify({"message": "Vui lòng nhập địa chỉ"}), 400
    
    lat, lng = geocode_address(address)
    if lat and lng:
        return jsonify({"address": address, "lat": lat, "lng": lng}), 200
    return jsonify({"message": "Không tìm thấy tọa độ cho địa chỉ này"}), 404

# ============================
# GET NEARBY
# ============================
@bp.route("/nearby", methods=["GET"])
def nearby_branches():
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
        radius_m = float(request.args.get("radius_m"))
    except (TypeError, ValueError):
        return jsonify({
            "message": "lat, lng, radius_m phải là số"
        }), 400

    result = find_nearby_branches(lat, lng, radius_m)
    return jsonify(result)

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
