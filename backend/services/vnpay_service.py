from db import get_conn
from datetime import datetime
from services.transaction_service import generate_sequential_id

def create_payment(account_id, amount, provider):
    conn = get_conn()
    try:
        payment_id = generate_sequential_id("P", "PAYMENT", "PAYMENT_ID", conn=conn)

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO PAYMENT (PAYMENT_ID, ACCOUNT_ID, AMOUNT, PROVIDER, STATUS, CREATED_AT)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                payment_id,
                account_id,
                amount,
                provider,
                "PENDING",
                datetime.now()
            ))
        conn.commit()

        return payment_id
    finally:
        conn.close()
