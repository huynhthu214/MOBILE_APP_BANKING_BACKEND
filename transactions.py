from flask import Blueprint, request, jsonify
from db import get_connection
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

# Lấy danh sách giao dịch
@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.BillId, b.Amount, b.Status, b.CreatedDate, a.Email AS CustomerEmail
        FROM Bill b
        LEFT JOIN Account a ON b.CustomerId = a.CustomerId
    """)
    bills = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(bills)

# Tạo giao dịch mới
@transactions_bp.route('/', methods=['POST'])
def create_transaction():
    data = request.json
    customer_id = data.get('customer_id')
    amount = data.get('amount')
    status = data.get('status', 'Processing')

    if not all([customer_id, amount]):
        return jsonify({'error': 'Thiếu thông tin'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Bill (CustomerId, Amount, Status, CreatedDate)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, amount, status, datetime.now()))
        conn.commit()
        return jsonify({'message': 'Tạo giao dịch thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Cập nhật trạng thái giao dịch
@transactions_bp.route('/<int:bill_id>', methods=['PUT'])
def update_transaction(bill_id):
    data = request.json
    status = data.get('status')

    if not status:
        return jsonify({'error': 'Cần cung cấp status'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Bill SET Status=%s WHERE BillId=%s", (status, bill_id))
        conn.commit()
        return jsonify({'message': 'Cập nhật trạng thái thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
