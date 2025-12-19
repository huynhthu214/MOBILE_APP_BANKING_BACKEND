# models/transaction_model.py
from db import get_conn
from datetime import datetime


<<<<<<< HEAD
class TransactionModel:
    TABLE_NAME = "TRANSACTION"

    @staticmethod
    def generate_transaction_id():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT TRANSACTION_ID FROM `TRANSACTION` ORDER BY TRANSACTION_ID DESC LIMIT 1")
                last = cur.fetchone()
                if last and last["TRANSACTION_ID"]:
                    num = int(last["TRANSACTION_ID"][1:]) + 1
                    return f"T{num:04d}"
                return "T0001"
        finally:
            conn.close()

    @staticmethod
    def create(
        account_id,
        amount,
        tx_type,
        status="PENDING",
        payment_id=None,
        dest_acc_num=None,
        dest_acc_name=None,
        dest_bank_code=None,
        currency="VND",
        account_type="checking"
    ):
        transaction_id = TransactionModel.generate_transaction_id()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {TransactionModel.TABLE_NAME}
                    (TRANSACTION_ID, PAYMENT_ID, ACCOUNT_ID, AMOUNT, CURRENCY,
                     ACCOUNT_TYPE, STATUS, CREATED_AT, COMPLETE_AT,
                     DEST_ACC_NUM, DEST_ACC_NAME, DEST_BANK_CODE, TYPE)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),NULL,%s,%s,%s,%s)
                """, (
                    transaction_id,
                    payment_id,
                    account_id,
                    amount,
                    currency,
                    account_type,
                    status,
                    dest_acc_num,
                    dest_acc_name,
                    dest_bank_code,
                    tx_type
                ))
                conn.commit()
                return transaction_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(transaction_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {TransactionModel.TABLE_NAME} WHERE TRANSACTION_ID=%s",
                    (transaction_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def list_all(account_id=None):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if account_id:
                    cur.execute(
                        f"""SELECT * FROM {TransactionModel.TABLE_NAME}
                            WHERE ACCOUNT_ID=%s
                            ORDER BY CREATED_AT DESC""",
                        (account_id,)
                    )
                else:
                    cur.execute(
                        f"SELECT * FROM {TransactionModel.TABLE_NAME} ORDER BY CREATED_AT DESC"
                    )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update_status(transaction_id, status):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE {TransactionModel.TABLE_NAME}
                    SET STATUS=%s, COMPLETE_AT=NOW()
                    WHERE TRANSACTION_ID=%s
                """, (status, transaction_id))
                conn.commit()
        finally:
            conn.close()
=======
# ============================================================
# GET ALL / FILTER
# ============================================================
def get_transactions(account_id=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if account_id:
                cur.execute("""
                    SELECT * FROM `TRANSACTION`
                    WHERE ACCOUNT_ID = %s
                    ORDER BY CREATED_AT DESC
                """, (account_id,))
            else:
                cur.execute("SELECT * FROM `TRANSACTION` ORDER BY CREATED_AT DESC")

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
            cur.execute("""
                SELECT * FROM `TRANSACTION`
                WHERE TRANSACTION_ID = %s
            """, (transaction_id,))
            return cur.fetchone()
    finally:
        conn.close()


# ============================================================
# CREATE TRANSACTION (deposit / withdraw / transfer)
# ============================================================
def create_transaction(
    transaction_id,
    account_id,
    amount,
    tx_type,
    status="PENDING",
    dest_acc_num=None,
    dest_acc_name=None,
    dest_bank_code=None,
    currency="VND",
    account_type="checking",
    payment_id=None
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO `TRANSACTION` (
                    TRANSACTION_ID,
                    PAYMENT_ID,
                    ACCOUNT_ID,
                    AMOUNT,
                    CURRENCY,
                    ACCOUNT_TYPE,
                    STATUS,
                    CREATED_AT,
                    COMPLETE_AT,
                    DEST_ACC_NUM,
                    DEST_ACC_NAME,
                    DEST_BANK_CODE,
                    TYPE
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NULL, %s, %s, %s, %s)
            """, (
                transaction_id,
                payment_id,
                account_id,
                amount,
                currency,
                account_type,
                status,
                dest_acc_num,
                dest_acc_name,
                dest_bank_code,
                tx_type
            ))
            conn.commit()
    finally:
        conn.close()


# ============================================================
# UPDATE STATUS
# ============================================================
def update_transaction_status(transaction_id, status):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE `TRANSACTION`
                SET STATUS = %s,
                    COMPLETE_AT = NOW()
                WHERE TRANSACTION_ID = %s
            """, (status, transaction_id))
            conn.commit()
    finally:
        conn.close()


# ============================================================
# ACCOUNT SUPPORT
# ============================================================
def get_account(account_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s", (account_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_account_by_number(account_number):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_NUMBER = %s", (account_number,))
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
                    WHERE ACCOUNT_ID = %s
                """, (amount, account_id))
            else:
                cur.execute("""
                    UPDATE ACCOUNT
                    SET BALANCE = BALANCE - %s
                    WHERE ACCOUNT_ID = %s
                """, (amount, account_id))

            conn.commit()
    finally:
        conn.close()


# ============================================================
# OTP SUPPORT
# ============================================================
def get_valid_otp(user_id, code):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM OTP
                WHERE USER_ID = %s
                  AND CODE = %s
                  AND IS_USED = 0
                  AND EXPIRES_AT > NOW()
            """, (user_id, code))
            return cur.fetchone()
    finally:
        conn.close()


def mark_otp_used(otp_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE OTP SET IS_USED = 1 WHERE OTP_ID = %s", (otp_id,))
            conn.commit()
    finally:
        conn.close()
>>>>>>> 3613aca5a3aa4a331c9e6ff98f354b06b893c610
