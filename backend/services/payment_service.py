# services/payment_service.py
import uuid
from datetime import datetime
from db import get_conn
from utils import generate_sequential_id

def create_payment(account_id, amount, provider, payment_type):
    payment_id = str(uuid.uuid4())
    conn = get_conn()
    try:
        # Quan trọng: Đảm bảo autocommit được tắt để quản lý thủ công
        conn.autocommit = False 
        
        with conn.cursor() as cur:
            sql = """
                INSERT INTO PAYMENT (
                    PAYMENT_ID, ACCOUNT_ID, AMOUNT, PROVIDER, TYPE, STATUS, CREATED_AT
                )
                VALUES (%s, %s, %s, %s, %s, 'PENDING', %s)
            """
            params = (payment_id, account_id, amount, provider, payment_type, datetime.now())
            cur.execute(sql, params)
        
        # PHẢI GỌI COMMIT Ở ĐÂY
        conn.commit() 
        print(f"--- DB SUCCESS: Da luu payment_id {payment_id} ---")

    except Exception as e:
        conn.rollback() # Hoàn tác nếu có lỗi
        print(f"--- DB ERROR: {str(e)} ---")
        raise e
    finally:
        conn.close()

    # Trả về URL cho Android
    host_url = "http://10.0.2.2:5000"
    return {
        "payment_id": payment_id,
        "payment_url": f"{host_url}/api/v1/payments/mock-view/{payment_id}"
    }