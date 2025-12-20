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

# API: Đánh dấu đã đọc (Option thêm cho bạn)
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