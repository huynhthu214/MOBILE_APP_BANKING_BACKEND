
# models/payment_model.py
from db import get_conn
from datetime import datetime

# =============================
# BILL
# =============================
def get_bills(keyword=""):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM BILL"
            if keyword:
                sql += " WHERE PROVIDER LIKE %s OR STATUS LIKE %s"
                cur.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
            else:
                cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()

def get_bill_by_id(bill_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM BILL WHERE BILL_ID=%s", (bill_id,))
            return cur.fetchone()
    finally:
        conn.close()

def update_bill_status(bill_id, status):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE BILL SET STATUS=%s WHERE BILL_ID=%s", (status, bill_id))
            conn.commit()
    finally:
        conn.close()

# =============================
# BILL PAYMENT
# =============================
def create_bill_payment(payment_id, transaction_id, bill_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            paid_at = datetime.now()
            cur.execute("""
                INSERT INTO BILL_PAYMENT (PAYMENT_ID, TRANSACTION_ID, BILL_ID, PAID_AT)
                VALUES (%s, %s, %s, %s)
            """, (payment_id, transaction_id, bill_id, paid_at))
            conn.commit()
    finally:
        conn.close()

# =============================
# TRANSACTION
# =============================
def create_transaction(transaction_id, account_id, amount, currency="VND", tx_type="BILL_PAYMENT"):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            created_at = datetime.now()
            cur.execute("""
                INSERT INTO TRANSACTIONS (TRANSACTION_ID, ACCOUNT_ID, AMOUNT, CURRENCY, STATUS, CREATED_AT, TYPE)
                VALUES (%s, %s, %s, %s, 'SUCCESS', %s, %s)
            """, (transaction_id, account_id, amount, currency, created_at, tx_type))
            conn.commit()
    finally:
        conn.close()

# =============================
# ACCOUNT
# =============================
def get_account(account_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID=%s", (account_id,))
            return cur.fetchone()
    finally:
        conn.close()

def update_account_balance(account_id, amount):
    """
    Trừ số tiền từ account
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE ACCOUNT SET BALANCE = BALANCE - %s WHERE ACCOUNT_ID=%s", (amount, account_id))
            conn.commit()
    finally:
        conn.close()

# =============================
# UTILITY PAYMENT
# =============================
def create_utility_payment(utility_payment_id, transaction_id, provider_code, ref1, ref2):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            created_at = datetime.now()
            cur.execute("""
                INSERT INTO UTILITY_PAYMENT 
                (UTILITY_PAYMENT_ID, TRANSACTION_ID, PROVIDER_CODE, REFERENCE_CODE_1, REFERENCE_CODE_2, CREATED_AT)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (utility_payment_id, transaction_id, provider_code, ref1, ref2, created_at))
            conn.commit()
    finally:
        conn.close()
