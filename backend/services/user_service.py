# backend/services/user_service.py
from db import get_conn
from werkzeug.security import generate_password_hash
import datetime

# --- Helpers ---
def fetch_user_by_email(email):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USER WHERE EMAIL=%s LIMIT 1", (email,))
            return cur.fetchone()
    finally:
        conn.close()

def fetch_user_by_id(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USER WHERE USER_ID=%s LIMIT 1", (user_id,))
            return cur.fetchone()
    finally:
        conn.close()

def generate_next_user_id():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT USER_ID FROM USER ORDER BY USER_ID DESC LIMIT 1")
            last = cur.fetchone()
            if last:
                last_id = last['USER_ID']
                return f"U{int(last_id[1:]) + 1:03d}"
            else:
                return "U001"
    finally:
        conn.close()


# =========================
#  SERVICE: USER MANAGEMENT
# =========================

def create_user(data):
    if not data:
        return {"status":"error","message":"Invalid JSON body","status_code":400}

    full_name = data.get('FULL_NAME')
    email = data.get('EMAIL')
    phone = data.get('PHONE')
    password = data.get('PASSWORD')
    role = data.get('ROLE', 'user')

    if not all([full_name, email, password]):
        return {"status":"error","message":"FULL_NAME, EMAIL, PASSWORD required","status_code":400}

    if fetch_user_by_email(email):
        return {"status":"error","message":"email already exists","status_code":400}

    user_id = generate_next_user_id()
    hashed_pwd = generate_password_hash(password)

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO USER (USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, CREATED_AT, IS_ACTIVE, PASSWORD_HASH)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id, full_name, email, phone,
                role, datetime.datetime.now(), True, hashed_pwd
            ))
            conn.commit()
    finally:
        conn.close()

    return {
        "status": "success",
        "message": "user created",
        "USER_ID": user_id,
        "status_code": 201
    }


def get_user_detail(user_id):
    user = fetch_user_by_id(user_id)
    if not user:
        return {"status":"error","message":"User not found","status_code":404}

    user.pop("PASSWORD_HASH", None)
    return {"status":"success","data": user}


def update_user_info(user_id, data):
    user = fetch_user_by_id(user_id)
    if not user:
        return {"status":"error","message":"User not found","status_code":404}

    full_name = data.get("FULL_NAME", user["FULL_NAME"])
    phone = data.get("PHONE", user["PHONE"])
    role = data.get("ROLE", user["ROLE"])
    is_active = data.get("IS_ACTIVE", user["IS_ACTIVE"])

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE USER 
                SET FULL_NAME=%s, PHONE=%s, ROLE=%s, IS_ACTIVE=%s
                WHERE USER_ID=%s
            """, (full_name, phone, role, is_active, user_id))
            conn.commit()
    finally:
        conn.close()

    return {"status":"success","message":"User updated"}


def list_users(keyword=""):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM USER
                WHERE FULL_NAME LIKE %s OR EMAIL LIKE %s
                ORDER BY CREATED_AT DESC
            """, (f"%{keyword}%", f"%{keyword}%"))
            users = cur.fetchall()
    finally:
        conn.close()

    for u in users:
        u.pop("PASSWORD_HASH", None)

    return {"status":"success","data": users}

def search_users(keyword):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
        SELECT USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, IS_ACTIVE
        FROM USER
        WHERE FULL_NAME LIKE %s
           OR EMAIL LIKE %s
           OR PHONE LIKE %s
    """

    key = f"%{keyword}%"
    cursor.execute(sql, (key, key, key))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data