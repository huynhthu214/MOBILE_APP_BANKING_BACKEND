# services/payment_callback_service.py
from db import get_conn
from datetime import datetime
from utils import generate_sequential_id

def handle_payment_callback(payment_id, result):
    conn = get_conn()
    try:
        # Bắt đầu transaction DB
        conn.autocommit = False 
        
        cursor = conn.cursor() # Dùng cursor dict nếu cấu hình db của bạn hỗ trợ

        # 1. Lấy payment
        cursor.execute("SELECT * FROM PAYMENT WHERE PAYMENT_ID = %s FOR UPDATE", (payment_id,))
        payment = cursor.fetchone()

        if not payment:
            conn.rollback()
            return {"status": "error", "message": "Payment not found"}

        # Kiểm tra nếu payment là dict (RealDictCursor) hay tuple
        # Code dưới giả định là Dict, nếu là Tuple hãy sửa lại chỉ số [index]
        status = payment['STATUS'] if isinstance(payment, dict) else payment[5] 

        if status != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Payment already processed"}

        account_id = payment['ACCOUNT_ID'] if isinstance(payment, dict) else payment[1]
        amount = payment['AMOUNT'] if isinstance(payment, dict) else payment[2]
        
        # 2. Xử lý thất bại
        if result != "success":
            cursor.execute("UPDATE PAYMENT SET STATUS=%s WHERE PAYMENT_ID=%s", ("FAILED", payment_id))
            conn.commit()
            return {"status": "failed"}

        # 3. Xử lý thành công -> CỘNG TIỀN
        cursor.execute("UPDATE ACCOUNT SET BALANCE = BALANCE + %s WHERE ACCOUNT_ID = %s", (amount, account_id))

        # 4. GHI TRANSACTION
        # Tạo Transaction ID mới
        tx_id = generate_sequential_id("TRANSACTIONS", "T", "TRANSACTION_ID")
        
        cursor.execute("""
            INSERT INTO TRANSACTIONS (TRANSACTION_ID, ACCOUNT_ID, AMOUNT, CURRENCY, TYPE, STATUS, CREATED_AT)
            VALUES (%s, %s, %s, 'VND', 'DEPOSIT', 'COMPLETED', %s)
        """, (tx_id, account_id, amount, datetime.now()))

        # 5. UPDATE PAYMENT STATUS
        cursor.execute("UPDATE PAYMENT SET STATUS=%s WHERE PAYMENT_ID=%s", ("SUCCESS", payment_id))

        conn.commit()
        return {"status": "success"}

    except Exception as e:
        conn.rollback()
        print("[PAYMENT CALLBACK ERROR]", e)
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()