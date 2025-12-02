from flask import Blueprint, request, jsonify
from services.file_upload import save_file

bp = Blueprint("files", __name__, url_prefix="/api/v1/files")

@bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status":"error","message":"No file"}), 400

    file = request.files["file"]
    path = save_file(file)

    return jsonify({
        "status":"success",
        "file_url": path
    }), 201
