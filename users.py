from flask import Blueprint, request, jsonify
from db import get_connection

users_bp = Blueprint('users', __name__)

# Lấy danh sách người dùng
@users_bp.route('/', methods=['GET'])
def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, IS_ACTIVE FROM USER")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    # Chuyển tuple sang dict để JSON dễ đọc
    users_list = []
    for u in users:
        users_list.append({
            'user_id': u[0],
            'full_name': u[1],
            'email': u[2],
            'phone': u[3],
            'role': u[4],
            'is_active': bool(u[5])
        })
    return jsonify(users_list)

# Update thông tin user
@users_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    full_name = data.get('full_name')
    phone = data.get('phone')
    role = data.get('role')
    is_active = data.get('is_active')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE USER
            SET FULL_NAME=%s, PHONE=%s, ROLE=%s, IS_ACTIVE=%s
            WHERE USER_ID=%s
        """, (full_name, phone, role, is_active, user_id))
        conn.commit()
        return jsonify({'message': 'Cập nhật user thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
