# models/utility_model.py
from db import get_conn


class UtilityPaymentModel:
    TABLE_NAME = "UTILITY_PAYMENT"

    @staticmethod
    def generate_utility_payment_id():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT UTILITY_PAYMENT_ID
                    FROM UTILITY_PAYMENT
                    ORDER BY UTILITY_PAYMENT_ID DESC
                    LIMIT 1
                """)
                last = cur.fetchone()
                if last and last["UTILITY_PAYMENT_ID"]:
                    num = int(last["UTILITY_PAYMENT_ID"][2:]) + 1
                    return f"UP{num:04d}"
                return "UP0001"
        finally:
            conn.close()

    @staticmethod
    def create(transaction_id, provider_code, ref1=None, ref2=None):
        utility_payment_id = UtilityPaymentModel.generate_utility_payment_id()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {UtilityPaymentModel.TABLE_NAME}
                    (UTILITY_PAYMENT_ID, TRANSACTION_ID, PROVIDER_CODE,
                     REFERENCE_CODE_1, REFERENCE_CODE_2, CREATED_AT)
                    VALUES (%s,%s,%s,%s,%s,NOW())
                """, (
                    utility_payment_id,
                    transaction_id,
                    provider_code,
                    ref1,
                    ref2
                ))
                conn.commit()
                return utility_payment_id
        finally:
            conn.close()

    @staticmethod
    def get_by_id(payment_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT up.*, t.AMOUNT, t.STATUS AS TRANSACTION_STATUS
                    FROM UTILITY_PAYMENT up
                    JOIN `TRANSACTION` t
                      ON t.TRANSACTION_ID = up.TRANSACTION_ID
                    WHERE up.UTILITY_PAYMENT_ID=%s
                """, (payment_id,))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def list_all():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT up.*, t.AMOUNT
                    FROM UTILITY_PAYMENT up
                    JOIN `TRANSACTION` t
                      ON t.TRANSACTION_ID = up.TRANSACTION_ID
                    ORDER BY up.CREATED_AT DESC
                """)
                return cur.fetchall()
        finally:
            conn.close()
