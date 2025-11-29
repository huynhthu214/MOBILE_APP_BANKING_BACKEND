from flask import Blueprint, request, jsonify
from db import get_connection
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

# Lấy danh sách tất cả payment
@payments_bp.route('/', methods=['GET'])
def get_payments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT PAYMENT_ID, BillId, PaymentMethod, Amount, PaymentDate
        FROM Bill_Payment
    """)
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(payments)

# Tạo payment mới
@payments_bp.route('/', methods=['POST'])
def create_payment():
    data = request.json
    bill_id = data.get('bill_id')
    payment_method = data.get('payment_method')
    amount = data.get('amount')

    if not all([bill_id, payment_method, amount]):
        return jsonify({'error': 'Thiếu thông tin'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Bill_Payment (BillId, PaymentMethod, Amount, PaymentDate)
            VALUES (%s, %s, %s, %s)
        """, (bill_id, payment_method, amount, datetime.now()))
        conn.commit()
        return jsonify({'message': 'Thanh toán được tạo thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Cập nhật payment
@payments_bp.route('/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.json
    payment_method = data.get('payment_method')
    amount = data.get('amount')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Bill_Payment
            SET PaymentMethod=%s, Amount=%s
            WHERE PAYMENT_ID=%s
        """, (payment_method, amount, payment_id))
        conn.commit()
        return jsonify({'message': 'Cập nhật payment thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Xóa payment
@payments_bp.route('/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Bill_Payment WHERE PAYMENT_ID=%s", (payment_id,))
        conn.commit()
        return jsonify({'message': 'Xóa payment thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
