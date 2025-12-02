from db import get_conn

def generate_otp_id():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT OTP_ID FROM OTP ORDER BY OTP_ID DESC LIMIT 1")
            last = cur.fetchone()
            if last and last["OTP_ID"]:
                num = int(last["OTP_ID"][1:]) + 1
                return f"O{num:03d}"
            return "O001"
    finally:
        conn.close()
class OTPModel:
    TABLE_NAME = "OTP"

    @staticmethod
    def create(user_id, code, purpose, expires_at):
        otp_id = generate_otp_id()

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

        return otp_id
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
