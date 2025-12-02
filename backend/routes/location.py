from flask import Blueprint, request, jsonify
from services.location_service import (
    create_branch,
    get_all_branches,
    get_branch_by_id,
    update_branch,
    delete_branch
)

bp = Blueprint("location", __name__, url_prefix="/api/v1/branches")


# ============================
# POST /api/v1/branches
# ============================
@bp.route("", methods=["POST"])
def create():
    data = request.json
    result = create_branch(data)
    return jsonify(result)


# ============================
# GET /api/v1/branches
# ============================
@bp.route("", methods=["GET"])
def get_all():
    result = get_all_branches()
    return jsonify({
        "message": "success",
        "data": result
    })


# ============================
# GET /api/v1/branches/{id}
# ============================
@bp.route("/<branch_id>", methods=["GET"])
def get_one(branch_id):
    result = get_branch_by_id(branch_id)

    if not result:
        return jsonify({"message": "not_found"}), 404

    return jsonify({
        "message": "success",
        "data": result
    })


# ============================
# PUT /api/v1/branches/{id}
# ============================
@bp.route("/<branch_id>", methods=["PUT"])
def update(branch_id):
    data = request.json
    result = update_branch(branch_id, data)
    return jsonify(result)


# ============================
# DELETE /api/v1/branches/{id}
# ============================
@bp.route("/<branch_id>", methods=["DELETE"])
def delete(branch_id):
    result = delete_branch(branch_id)
    return jsonify(result)
