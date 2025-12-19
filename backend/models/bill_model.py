# models/bill_model.py
from db import get_conn


class BillModel:
    TABLE_NAME = "BILL"

    @staticmethod
    def generate_bill_id():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT BILL_ID FROM BILL ORDER BY BILL_ID DESC LIMIT 1")
                last = cur.fetchone()
                if last and last["BILL_ID"]:
                    num = int(last["BILL_ID"][1:]) + 1
                    return f"B{num:04d}"
                return "B0001"
        finally:
            conn.close()

    @staticmethod
    def create(user_id, provider_code, amount, due_date, status="UNPAID"):
        bill_id = BillModel.generate_bill_id()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {BillModel.TABLE_NAME}
                    (BILL_ID, USER_ID, PROVIDER_CODE, AMOUNT, DUE_DATE, STATUS, CREATED_AT)
                    VALUES (%s,%s,%s,%s,%s,%s,NOW())
                """, (
                    bill_id,
                    user_id,
                    provider_code,
                    amount,
                    due_date,
                    status
                ))
                conn.commit()
                return bill_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(bill_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {BillModel.TABLE_NAME} WHERE BILL_ID=%s",
                    (bill_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def list_all(user_id=None):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                if user_id:
                    cur.execute(
                        f"SELECT * FROM {BillModel.TABLE_NAME} WHERE USER_ID=%s ORDER BY CREATED_AT DESC",
                        (user_id,)
                    )
                else:
                    cur.execute(
                        f"SELECT * FROM {BillModel.TABLE_NAME} ORDER BY CREATED_AT DESC"
                    )
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update_status(bill_id, status):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {BillModel.TABLE_NAME} SET STATUS=%s WHERE BILL_ID=%s",
                    (status, bill_id)
                )
                conn.commit()
        finally:
            conn.close()
