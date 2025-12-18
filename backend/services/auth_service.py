from models.user_model import get_user_by_id, get_user_by_email, update_user_password
from services.security_utils import (
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    revoke_refresh_token,
    blacklist_access_token,
    decode_access_token
)
from services.otp_service import create_otp, verify_otp_util
from db import get_conn
import jwt
from config import JWT_SECRET, JWT_ALGORITHM


# ========================
# AUTH SERVICES
# ========================

def login(data):
    if not data:
        return {"status":"error","message":"Invalid JSON body","status_code":400}
    
    email = data.get('email')
    password = data.get('password')
    require_otp = data.get('require_otp', False)

    if not email or not password:
        return {"status":"error","message":"email and password required","status_code":400}

    user = get_user_by_email(email)
    if not user:
        return {"status":"error","message":"invalid credentials","status_code":401}

    if not user.get('IS_ACTIVE', 1):
        return {"status":"error","message":"account inactive","status_code":403}

    # So sánh trực tiếp password
    if password != user.get('PASSWORD'):
        return {"status":"error","message":"invalid credentials","status_code":401}

    # Login có OTP
    if require_otp:
        otp_id, code = create_otp(user['USER_ID'], purpose='login')
        return {
            "status":"success",
            "data":{
                "requires_otp": True,
                "otp_id": otp_id,
                "otp_code_dev": code
            }
        }

    access_token = create_access_token(user['USER_ID'], user.get('ROLE'))
    refresh_token, expires = create_refresh_token(user['USER_ID'])
    store_refresh_token(user['USER_ID'], refresh_token, expires)

    safe_user = {k: v for k, v in user.items() if k != 'PASSWORD'}

    return {
        "status":"success",
        "data":{
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": safe_user
        }
    }


def logout(data, auth_header=None):
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return {"status":"error","message":"refresh_token required","status_code":400}

    user_id = None
    if auth_header and auth_header.startswith('Bearer '):
        access = auth_header.split(' ')[1]
        payload, err = decode_access_token(access)
        if not err:
            user_id = payload.get("sub")
            blacklist_access_token(access)

    if user_id:
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE REFRESH_TOKEN SET REVOKED=1 WHERE TOKEN=%s AND USER_ID=%s",
                    (refresh_token, user_id)
                )
            conn.commit()
        finally:
            conn.close()

    return {"status":"success","message":"logged out"}


def refresh(data):
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return {"status":"error","message":"refresh_token required","status_code":400}

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM REFRESH_TOKEN WHERE TOKEN=%s AND REVOKED=0 LIMIT 1",
                (refresh_token,)
            )
            row = cur.fetchone()

            if not row:
                return {
                    "status":"error",
                    "message":"refresh token invalid or revoked",
                    "status_code":401
                }
    finally:
        conn.close()

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('type') != 'refresh':
            return {"status":"error","message":"invalid token type","status_code":401}
    except jwt.ExpiredSignatureError:
        return {"status":"error","message":"refresh token expired","status_code":401}
    except Exception:
        return {"status":"error","message":"invalid token","status_code":401}

    user_id = payload.get('sub')

    revoke_refresh_token(refresh_token)
    new_refresh, new_expires = create_refresh_token(user_id)
    store_refresh_token(user_id, new_refresh, new_expires)

    user = get_user_by_id(user_id)
    role = user.get('ROLE') if user else None

    new_access = create_access_token(user_id, role)

    return {
        "status":"success",
        "data":{
            "access_token": new_access,
            "refresh_token": new_refresh
        }
    }


# --- Change password ---
def change_password(user_id, data):
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return {"status":"error","message":"old_password and new_password required","status_code":400}

    user = get_user_by_id(user_id)
    if not user:
        return {"status":"error","message":"User not found","status_code":404}

    # So sánh trực tiếp với cột PASSWORD_HASH
    if old_password != user.get('PASSWORD'):
        return {"status":"error","message":"Old password incorrect","status_code":401}

    # Update password mới
    update_user_password(user_id, new_password)

    return {"status":"success","message":"Password changed successfully"}


def forgot_password(data):
    email = data.get('email')
    if not email:
        return {"status":"error","message":"Email required","status_code":400}

    user = get_user_by_email(email)
    if not user:
        return {"status":"error","message":"User not found","status_code":404}

    otp_id, code = create_otp(user['USER_ID'], purpose='forgot_password')

    return {
        "status":"success",
        "message":"OTP sent",
        "data": {
            "user_id": user['USER_ID'],
            "otp_id": otp_id,
            "otp_code_dev": code
        }
    }

def reset_password(data):
    user_id = data.get('user_id')   # sửa dòng này
    otp_code = data.get('otp_code')
    new_password = data.get('new_password')

    if not user_id or not otp_code or not new_password:
        return {"status":"error","message":"Missing fields","status_code":400}

    ok, msg = verify_otp_util(user_id, otp_code, purpose='forgot_password')

    if not ok:
        return {"status":"error","message":msg,"status_code":400}

    update_user_password(user_id, new_password)
    return {"status":"success","message":"Password reset successfully"}
