from flask import Blueprint, request, jsonify
from services.file_upload import save_file_base64, delete_file

bp = Blueprint("files", __name__, url_prefix="/api/v1/files")


@bp.route("/upload/base64", methods=["POST"])
def upload_base64():
    data = request.get_json()
    file_base64 = data.get("file")

    if not file_base64:
        return jsonify({"status":"error","message":"Missing file base64"}), 400

    path = save_file_base64(file_base64)

    if not path:
        return jsonify({"status":"error","message":"Invalid base64"}), 400

    return jsonify({
        "status": "success",
        "file_url": path
    }), 201


@bp.route("/<filename>", methods=["DELETE"])
def delete_file_route(filename):
    ok = delete_file(filename)

    if not ok:
        return jsonify({"status":"error","message":"File not found"}), 404

    return jsonify({
        "status":"success",
        "message":"File deleted"
    }), 200
