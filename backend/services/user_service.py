from models.user_model import (
    create_user as create_user_db,
    get_user_by_id,
    get_user_by_email,
    update_user as update_user_db,
    search_users as search_users_db,
    create_user_with_account_transaction
)
from db import get_conn

# =========================
#  SERVICE: ADMIN CREATE CUSTOMER (Dùng cho App Android)
# =========================

def create_customer_service(data):
    # 1. Validate
    if not data or not data.get('full_name') or not data.get('email') or not data.get('password'):
        return {"status": "error", "message": "Thiếu thông tin bắt buộc", "status_code": 400}

    # 2. Check trùng Email
    if get_user_by_email(data['email']):
        return {"status": "error", "message": "Email đã tồn tại", "status_code": 409}

    # 3. KHÔNG HASH PASSWORD (Lưu thô)
    plain_password = data['password']

    try:
        # 4. Chuẩn bị dữ liệu
        user_data = {
            "FULL_NAME": data['full_name'],
            "EMAIL": data['email'],
            "PHONE": data.get('phone'),
            "ROLE": "customer",
            "PASSWORD": plain_password, # <-- Lưu trực tiếp pass thô vào cột PASSWORD
            "IS_ACTIVE": 1
        }
        
        # 5. Gọi Transaction Model
        result_db = create_user_with_account_transaction(user_data)
        
        return {
            "status": "success", 
            "message": "Tạo khách hàng và tài khoản thành công",
            "data": result_db,
            "status_code": 201
        }
    except Exception as e:
        return {"status": "error", "message": f"Lỗi Server: {str(e)}", "status_code": 500}


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
                # Xử lý trường hợp last['USER_ID'] có thể là int hoặc str tùy driver
                last_id_str = str(last['USER_ID']) 
                if len(last_id_str) > 1:
                     return f"U{int(last_id_str[1:]) + 1:03d}"
                return "U001"
            else:
                return "U001"
    finally:
        conn.close()


# =========================
#  SERVICE: USER MANAGEMENT (Legacy / Các phần khác dùng)
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
    
    # Lưu thô
    create_user_db({
        "USER_ID": user_id,
        "FULL_NAME": full_name,
        "EMAIL": email,
        "PHONE": phone,
        "ROLE": role,
        "PASSWORD": password, # <-- Sửa key thành PASSWORD cho đúng DB
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

    # Ẩn mật khẩu khi trả về JSON
    user.pop("PASSWORD", None) 
    return {"status":"success","data": user}


def update_user_info(user_id, data):
    user = get_user_by_id(user_id)

    if not user:
        return {
            "status":"error",
            "message":"User not found",
            "status_code":404
        }
    new_email = data.get("email") or data.get("EMAIL") or user["EMAIL"]
    update_user_db(user_id, {
        "FULL_NAME": data.get("FULL_NAME", user["FULL_NAME"]),
        "PHONE": data.get("PHONE", user["PHONE"]),
        "ROLE": data.get("ROLE", user["ROLE"]),
        "IS_ACTIVE": data.get("IS_ACTIVE", user["IS_ACTIVE"]),
        "EMAIL": new_email
    })

    return {"status":"success","message":"User updated"}


def list_users(keyword=""):
    users = search_users_db(keyword)

    for u in users:
        # Ẩn mật khẩu
        u.pop("PASSWORD", None)

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

            # 4. Xoá password trước khi trả về client
            user.pop("PASSWORD", None)

            return {
                "user": user,
                "ekyc": ekyc,
                "accounts": accounts
            }, None

    finally:
        conn.close()