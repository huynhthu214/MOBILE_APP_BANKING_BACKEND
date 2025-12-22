from db import get_conn
from datetime import datetime

class OTPModel:
    TABLE_NAME = "OTP"

    @staticmethod
    def generate_otp_id():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # --- BƯỚC 1: Lấy số lớn nhất hiện có ---
                # Logic: Lọc các ID bắt đầu bằng 'OTP', cắt bỏ 3 ký tự đầu ('OTP'), chuyển thành số để sắp xếp
                cur.execute(f"""
                    SELECT OTP_ID 
                    FROM {OTPModel.TABLE_NAME} 
                    WHERE OTP_ID LIKE 'OTP%%' 
                    ORDER BY CAST(SUBSTRING(OTP_ID, 4) AS UNSIGNED) DESC 
                    LIMIT 1
                """)
                last = cur.fetchone()
                
                next_num = 1
                if last and last["OTP_ID"]:
                    try:
                        # Cắt bỏ 3 ký tự đầu "OTP" để lấy số
                        next_num = int(last["OTP_ID"][3:]) + 1
                    except ValueError:
                        next_num = 1

                # --- BƯỚC 2: Vòng lặp an toàn (Chống trùng ID) ---
                while True:
                    # Format thành OTP001 (khớp với code cũ của bạn)
                    new_id = f"OTP{next_num:03d}" 
                    
                    cur.execute(f"SELECT OTP_ID FROM {OTPModel.TABLE_NAME} WHERE OTP_ID = %s", (new_id,))
                    if cur.fetchone():
                        # Nếu ID đã tồn tại, tăng số lên và thử lại
                        next_num += 1
                    else:
                        return new_id
        finally:
            conn.close()

    @staticmethod
    def create(user_id, code, purpose, expires_at):
        # Gọi hàm sinh ID đã sửa ở trên
        otp_id = OTPModel.generate_otp_id()

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO {OTPModel.TABLE_NAME} 
                    (OTP_ID, USER_ID, CODE, PURPOSE, CREATED_AT, EXPIRES_AT, IS_USED)
                    VALUES (%s, %s, %s, %s, NOW(), %s, 0)
                """, (otp_id, user_id, code, purpose, expires_at))
                conn.commit()
                return otp_id
        finally:
            conn.close()

    @staticmethod
    def get_latest_valid_otp(user_id, purpose):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                sql = f"""
                    SELECT * FROM {OTPModel.TABLE_NAME} 
                    WHERE USER_ID = %s 
                    AND PURPOSE = %s 
                    AND IS_USED = 0 
                    AND EXPIRES_AT > NOW()
                    ORDER BY CREATED_AT DESC 
                    LIMIT 1
                """
                cur.execute(sql, (user_id, purpose))
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