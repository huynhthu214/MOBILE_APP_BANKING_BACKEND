from flask import Blueprint, request, jsonify
from db import get_connection

accounts_bp = Blueprint('accounts', __name__)

# Lấy danh sách account
@accounts_bp.route('/', methods=['GET'])
def get_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ACCOUNT_ID, USER_ID, ACCOUNT_TYPE, BALANCE, INTEREST_RATE, STATUS, ACCOUNT_NUMBER, CREATED_AT
        FROM ACCOUNT
    """)
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()

    accounts_list = []
    for a in accounts:
        accounts_list.append({
            'account_id': a[0],
            'user_id': a[1],
            'account_type': a[2],
            'balance': a[3],
            'interest_rate': a[4],
            'status': a[5],
            'account_number': a[6],
            'created_at': str(a[7])
        })
    return jsonify(accounts_list)

# Update thông tin account
@accounts_bp.route('/<account_id>', methods=['PUT'])
def update_account(account_id):
    data = request.json
    account_type = data.get('account_type')
    balance = data.get('balance')
    interest_rate = data.get('interest_rate')
    status = data.get('status')
    account_number = data.get('account_number')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ACCOUNT
            SET ACCOUNT_TYPE=%s, BALANCE=%s, INTEREST_RATE=%s, STATUS=%s, ACCOUNT_NUMBER=%s
            WHERE ACCOUNT_ID=%s
        """, (account_type, balance, interest_rate, status, account_number, account_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Account không tồn tại'}), 404
        return jsonify({'message': 'Cập nhật account thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Xóa account
@accounts_bp.route('/<account_id>', methods=['DELETE'])
def delete_account(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ACCOUNT WHERE ACCOUNT_ID=%s", (account_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Account không tồn tại'}), 404
        return jsonify({'message': 'Xóa account thành công'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# Lấy chi tiết account theo ACCOUNT_ID
@accounts_bp.route('/detail/<account_id>', methods=['GET'])
def get_account_detail(account_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ACCOUNT_ID, USER_ID, ACCOUNT_TYPE, BALANCE, INTEREST_RATE, STATUS, ACCOUNT_NUMBER, CREATED_AT
            FROM ACCOUNT
            WHERE ACCOUNT_ID=%s
        """, (account_id,))
        account = cursor.fetchone()
        if account:
            account_data = {
                'account_id': account[0],
                'user_id': account[1],
                'account_type': account[2],
                'balance': account[3],
                'interest_rate': account[4],
                'status': account[5],
                'account_number': account[6],
                'created_at': str(account[7])
            }
            return jsonify(account_data)
        else:
            return jsonify({'error': 'Account không tồn tại'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()
