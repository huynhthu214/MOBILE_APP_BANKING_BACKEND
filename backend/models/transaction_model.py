# models/transaction_model.py
from db import get_conn
from datetime import datetime

class TransactionModel:
    TABLE_NAME = "TRANSACTIONS"

    @staticmethod
    def generate_transaction_id():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # 'T' có 1 ký tự, nên cắt từ ký tự thứ 2 (SUBSTRING(TRANSACTION_ID, 2))
                cur.execute(f"""
                    SELECT TRANSACTION_ID 
                    FROM {TransactionModel.TABLE_NAME} 
                    WHERE TRANSACTION_ID LIKE 'T%%' 
                    ORDER BY CAST(SUBSTRING(TRANSACTION_ID, 2) AS UNSIGNED) DESC 
                    LIMIT 1
                """)
                last = cur.fetchone()
                
                next_num = 1
                if last and last["TRANSACTION_ID"]:
                    try:
                        # Cắt bỏ 1 ký tự đầu ("T")
                        next_num = int(last["TRANSACTION_ID"][1:]) + 1
                    except ValueError:
                        next_num = 1

                while True:
                    # :03d cho 3 chữ số
                    new_id = f"T{next_num:03d}" 
                    
                    cur.execute(f"SELECT TRANSACTION_ID FROM {TransactionModel.TABLE_NAME} WHERE TRANSACTION_ID = %s", (new_id,))
                    if cur.fetchone():
                        next_num += 1
                    else:
                        return new_id
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
        # Tạo ID mới bằng hàm đã sửa
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
    def get_by_account(account_id=None):
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