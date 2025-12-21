# routes/noti.py
from flask import Blueprint, jsonify, request
from services.noti_service import get_user_notifications, mark_read_service

# Khai báo Blueprint
bp = Blueprint("noti", __name__, url_prefix="/api/v1")

# API: Lấy danh sách thông báo
@bp.route("/notifications/<user_id>", methods=["GET"])
def get_notifications(user_id):
    try:
        data = get_user_notifications(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"message": "Lỗi server", "error": str(e)}), 500

@bp.route("/notifications/<user_id>/read", methods=["PUT"])
def mark_as_read(user_id):
    try:
        success = mark_read_service(user_id)
        if success:
            return jsonify({"message": "Đã đánh dấu đã đọc"}), 200
        else:
            return jsonify({"message": "Lỗi cập nhật"}), 500
    except Exception as e:
        return jsonify({"message": "Lỗi server", "error": str(e)}), 500
    
@bp.route("/notifications/mark-read/<noti_id>", methods=["PUT"])
def mark_single_read(noti_id):
    from models.noti_model import mark_single_as_read_model
    if mark_single_as_read_model(noti_id):
        return jsonify({"message": "Updated"}), 200
    return jsonify({"message": "Failed"}), 500