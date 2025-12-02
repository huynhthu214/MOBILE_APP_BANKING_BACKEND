from db import get_conn

class OTPModel:
    TABLE_NAME = "OTP"

    @staticmethod
    def create(otp_id, user_id, code, purpose, expires_at):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {OTPModel.TABLE_NAME} 
                    (OTP_ID, USER_ID, CODE, PURPOSE, CREATED_AT, EXPIRES_AT, IS_USED)
                    VALUES (%s, %s, %s, %s, NOW(), %s, 0)
                """, (otp_id, user_id, code, purpose, expires_at))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_latest(user_id, purpose):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT * FROM {OTPModel.TABLE_NAME}
                    WHERE USER_ID=%s AND PURPOSE=%s AND IS_USED=0
                    ORDER BY CREATED_AT DESC LIMIT 1
                """, (user_id, purpose))
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def mark_used(otp_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {OTPModel.TABLE_NAME} SET IS_USED=1 WHERE OTP_ID=%s", (otp_id,))
                conn.commit()
        finally:
            conn.close()

    @staticmethod
    def list_all():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {OTPModel.TABLE_NAME} ORDER BY CREATED_AT DESC")
                return cur.fetchall()
        finally:
            conn.close()
