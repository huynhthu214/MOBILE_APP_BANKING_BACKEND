from models.user_model import (
    create_user as create_user_db,
    get_user_by_id,
    get_user_by_email,
    update_user as update_user_db,
    search_users as search_users_db
)
from db import get_conn


# =========================
#  HELPERS
# =========================

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
        return {
            "status":"error",
            "message":"FULL_NAME, EMAIL, PASSWORD required",
            "status_code":400
        }

    if get_user_by_email(email):
        return {
            "status":"error",
            "message":"email already exists",
            "status_code":400
        }

    user_id = generate_next_user_id()
    plain_pwd = password

    create_user_db({
        "USER_ID": user_id,
        "FULL_NAME": full_name,
        "EMAIL": email,
        "PHONE": phone,
        "ROLE": role,
        "PASSWORD_HASH": plain_pwd,
        "IS_ACTIVE": 1
    })

    return {
        "status": "success",
        "message": "user created",
        "USER_ID": user_id,
        "status_code": 201
    }


def get_user_detail(user_id):
    user = get_user_by_id(user_id)

    if not user:
        return {
            "status":"error",
            "message":"User not found",
            "status_code":404
        }

    user.pop("PASSWORD_HASH", None)
    return {"status":"success","data": user}


def update_user_info(user_id, data):
    user = get_user_by_id(user_id)

    if not user:
        return {
            "status":"error",
            "message":"User not found",
            "status_code":404
        }

    update_user_db(user_id, {
        "FULL_NAME": data.get("FULL_NAME", user["FULL_NAME"]),
        "PHONE": data.get("PHONE", user["PHONE"]),
        "ROLE": data.get("ROLE", user["ROLE"]),
        "IS_ACTIVE": data.get("IS_ACTIVE", user["IS_ACTIVE"])
    })

    return {"status":"success","message":"User updated"}


def list_users(keyword=""):
    users = search_users_db(keyword)

    for u in users:
        u.pop("PASSWORD_HASH", None)

    return {"status":"success","data": users}


def search_users(keyword):
    return search_users_db(keyword)


# =========================
#  SERVICE: GET CURRENT USER (ME)
# =========================

def get_me(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:

            # 1. Lấy user
            cur.execute("SELECT * FROM USER WHERE USER_ID=%s LIMIT 1", (user_id,))
            user = cur.fetchone()

            if not user:
                return None, "User not found"

            # 2. Lấy EKYC (qua USER.EKYC_ID)
            ekyc = None
            if user.get("EKYC_ID"):
                cur.execute(
                    "SELECT * FROM EKYC WHERE EKYC_ID=%s LIMIT 1",
                    (user["EKYC_ID"],)
                )
                ekyc = cur.fetchone()

            # 3. Lấy danh sách tài khoản
            cur.execute(
                "SELECT * FROM ACCOUNT WHERE USER_ID=%s ORDER BY CREATED_AT DESC",
                (user_id,)
            )
            accounts = cur.fetchall()

            # 4. Xoá password trước khi trả về
            user.pop("PASSWORD_HASH", None)

            return {
                "user": user,
                "ekyc": ekyc,
                "accounts": accounts
            }, None

    finally:
        conn.close()
