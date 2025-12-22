from db import get_conn
import random
import string

def generate_account_number():
    return '99' + ''.join(random.choice(string.digits) for _ in range(8))

def create_user_with_account_transaction(user_data):
    conn = get_conn()
    try:
        conn.begin()
        with conn.cursor() as cur:
            # --- 1. TẠO USER ID (U001, U002...) ---
            cur.execute("SELECT USER_ID FROM USER ORDER BY USER_ID DESC LIMIT 1")
            last = cur.fetchone()
            if last:
                try:
                    # Lấy số từ ID (VD: U005 -> 5)
                    next_val = int(last['USER_ID'][1:]) + 1
                except:
                    next_val = 1
                user_id = f"U{next_val:03d}"
            else:
                user_id = "U001"

            # --- 2. INSERT VÀO BẢNG USER ---
            # SỬA QUAN TRỌNG: Cột là PASSWORD, không phải PASSWORD_HASH
            sql_user = """
                INSERT INTO USER 
                (USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, PASSWORD, IS_ACTIVE, CREATED_AT)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cur.execute(sql_user, (
                user_id,
                user_data["FULL_NAME"],
                user_data["EMAIL"],
                user_data.get("PHONE"),
                user_data.get("ROLE", "customer"),
                user_data["PASSWORD"],  # <-- Đã sửa đúng tên cột
                user_data.get("IS_ACTIVE", 1)
            ))

            # --- 3. INSERT VÀO BẢNG ACCOUNT (Mặc định là Checking) ---
            # Tạo Account ID: A + số của User (VD: A001)
            acc_id = "A" + user_id[1:] 
            acc_num = generate_account_number()

            # Các cột MORTAGE_ACC_ID, SAVING_ACC_ID để null
            sql_account = """
                INSERT INTO ACCOUNT 
                (ACCOUNT_ID, USER_ID, ACCOUNT_TYPE, BALANCE, INTEREST_RATE, STATUS, ACCOUNT_NUMBER, CREATED_AT)
                VALUES (%s, %s, 'CHECKING', 0, 0, 'ACTIVE', %s, NOW())
            """
            cur.execute(sql_account, (acc_id, user_id, acc_num))

        conn.commit()
        return {"user_id": user_id, "account_number": acc_num}

    except Exception as e:
        conn.rollback()
        print(f"DB Error: {str(e)}") # In lỗi ra để debug nếu có
        raise e
    finally:
        conn.close()
        
def create_user(data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO USER 
                (USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, PASSWORD_HASH, IS_ACTIVE, CREATED_AT)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                data["USER_ID"],
                data["FULL_NAME"],
                data["EMAIL"],
                data.get("PHONE"),
                data.get("ROLE", "user"),
                data["PASSWORD_HASH"],
                data.get("IS_ACTIVE", 1)
            ))
            conn.commit()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USER WHERE USER_ID=%s", (user_id,))
            return cur.fetchone()
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USER WHERE EMAIL=%s", (email,))
            return cur.fetchone()
    finally:
        conn.close()


def update_user(user_id, data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE USER 
                SET FULL_NAME=%s, PHONE=%s, ROLE=%s, IS_ACTIVE=%s, EMAIL=%s
                WHERE USER_ID=%s
            """, (
                data["FULL_NAME"],
                data.get("PHONE"),
                data.get("ROLE"),
                data.get("IS_ACTIVE", 1),
                data["EMAIL"],
                user_id
            ))
            conn.commit()
    finally:
        conn.close()


def search_users(keyword=""):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Tìm theo Tên, Email HOẶC User ID
            sql = """
                SELECT * FROM USER
                WHERE FULL_NAME LIKE %s 
                OR EMAIL LIKE %s
                OR USER_ID LIKE %s  
                ORDER BY CREATED_AT DESC
            """
            like_val = f"%{keyword}%"
            cur.execute(sql, (like_val, like_val, like_val))
            return cur.fetchall()
    finally:
        conn.close()
        
def update_user_password(user_id, hashed_password):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE USER SET PASSWORD=%s WHERE USER_ID=%s",
                (hashed_password, user_id)
            )
        conn.commit()
    finally:
        conn.close()