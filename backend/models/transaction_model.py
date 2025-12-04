# models/transaction_model.py
from db import get_conn
from datetime import datetime


# ============================================================
# GET ALL / FILTER
# ============================================================
def get_transactions(keyword=""):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            sql = "SELECT * FROM TRANSACTION"
            if keyword:
                sql += """
                    WHERE ACCOUNT_ID LIKE %s 
                    OR STATUS LIKE %s 
                    OR TYPE LIKE %s 
                    OR DEST_ACC_NUM LIKE %s
                """
                kw = f"%{keyword}%"
                cur.execute(sql, (kw, kw, kw, kw))
            else:
                cur.execute(sql)
            return cur.fetchall()
    finally:
        conn.close()


# ============================================================
# GET BY ID
# ============================================================
def get_transaction_by_id(transaction_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM TRANSACTION WHERE TRANSACTION_ID=%s",
                (transaction_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


# ============================================================
# CREATE – Deposit / Withdraw / Transfer
# ============================================================
def create_transaction(data):
    """
    data = {
        'TRANSACTION_ID', 'PAYMENT_ID', 'ACCOUNT_ID', 'AMOUNT',
        'CURRENCY', 'ACCOUNT_TYPE', 'STATUS', 'DEST_ACC_NUM',
        'DEST_ACC_NAME', 'DEST_BANK_CODE', 'TYPE'
    }
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO TRANSACTION (
                    TRANSACTION_ID, PAYMENT_ID, ACCOUNT_ID, AMOUNT,
                    CURRENCY, ACCOUNT_TYPE, STATUS, CREATED_AT,
                    COMPLETE_AT, DEST_ACC_NUM, DEST_ACC_NAME,
                    DEST_BANK_CODE, TYPE
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NULL, %s, %s, %s, %s)
            """, (
                data["transaction_id"],
                data.get("payment_id"),
                data["account_id"],
                data["amount"],
                data.get("currency", "VND"),
                data.get("account_type", "checking"),
                data.get("status", "PENDING"),
                data.get("dest_acc_num"),
                data.get("dest_acc_name"),
                data.get("dest_bank_code"),
                data["type"]
            ))
            conn.commit()
    finally:
        conn.close()


# ============================================================
# UPDATE STATUS (SUCCESS / FAILED)
# ============================================================
def update_transaction_status(transaction_id, status):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE TRANSACTION 
                SET STATUS=%s, COMPLETE_AT=NOW()
                WHERE TRANSACTION_ID=%s
            """, (status, transaction_id))
            conn.commit()
    finally:
        conn.close()


# ============================================================
# ACCOUNT – SUPPORT
# ============================================================
def get_account(account_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID=%s", (account_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_account_by_number(acc_number):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_NUMBER=%s", (acc_number,))
            return cur.fetchone()
    finally:
        conn.close()


def update_balance(account_id, amount, increase=True):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if increase:
                cur.execute("""
                    UPDATE ACCOUNT 
                    SET BALANCE = BALANCE + %s 
                    WHERE ACCOUNT_ID=%s
                """, (amount, account_id))
            else:
                cur.execute("""
                    UPDATE ACCOUNT 
                    SET BALANCE = BALANCE - %s 
                    WHERE ACCOUNT_ID=%s
                """, (amount, account_id))
            conn.commit()
    finally:
        conn.close()


# ============================================================
# OTP – verify
# ============================================================
def get_valid_otp(user_id, code):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            now = datetime.now()
            cur.execute("""
                SELECT * FROM OTP
                WHERE USER_ID=%s AND CODE=%s AND IS_USED=0 AND EXPIRES_AT > %s
            """, (user_id, code, now))
            return cur.fetchone()
    finally:
        conn.close()


def mark_otp_used(otp_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE OTP SET IS_USED=1 WHERE OTP_ID=%s", (otp_id,))
            conn.commit()
    finally:
        conn.close()
