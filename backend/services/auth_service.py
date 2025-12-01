# backend/auth/services/auth_service.py
from db import get_conn
from services.utils import (
    verify_password, create_access_token, create_refresh_token,
    store_refresh_token, revoke_refresh_token, blacklist_access_token,
    create_otp, verify_otp as verify_otp_util
)

import jwt
from config import JWT_SECRET, JWT_ALGORITHM


# ========================
# HELPERS (AUTH ONLY)
# ========================

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


# ========================
# SERVICES
# ========================

def login(data):
    if not data:
        return {"status":"error","message":"Invalid JSON body","status_code":400}
    
    email = data.get('email')
    password = data.get('password')
    require_otp = data.get('require_otp', False)

    if not email or not password:
        return {"status":"error","message":"email and password required","status_code":400}
    
    user = fetch_user_by_email(email)
    if not user:
        return {"status":"error","message":"invalid credentials","status_code":401}

    if not user.get('IS_ACTIVE', 1):
        return {"status":"error","message":"account inactive","status_code":403}

    if not verify_password(password, user.get('PASSWORD_HASH')):
        return {"status":"error","message":"invalid credentials","status_code":401}

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

    safe_user = {k: v for k, v in user.items() if k != 'PASSWORD_HASH'}
    return {
        "status":"success",
        "data":{
            "access_token":access_token,
            "refresh_token":refresh_token,
            "user":safe_user
        }
    }


def logout(data, auth_header=None):
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return {"status":"error","message":"refresh_token required","status_code":400}
    
    revoke_refresh_token(refresh_token)

    if auth_header and auth_header.startswith('Bearer '):
        access = auth_header.split(' ')[1]
        blacklist_access_token(access)

    return {"status":"success","message":"logged out"}


def refresh(data):
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return {"status":"error","message":"refresh_token required","status_code":400}

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM REFRESH_TOKENS WHERE TOKEN=%s AND REVOKED=0 LIMIT 1",
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

    user = fetch_user_by_id(user_id)
    role = user.get('ROLE') if user else None

    new_access = create_access_token(user_id, role)

    return {
        "status":"success",
        "data":{
            "access_token": new_access,
            "refresh_token": new_refresh
        }
    }


def send_otp(data):
    user_id = data.get('USER_ID')
    purpose = data.get('PURPOSE', 'transaction')
    if not user_id:
        return {"status":"error","message":"USER_ID required","status_code":400}

    otp_id, code = create_otp(user_id, purpose=purpose)
    return {
        "status":"success",
        "data":{"otp_id": otp_id, "otp_code_dev": code}
    }


def verify_otp(data):
    user_id = data.get('USER_ID')
    code = data.get('CODE')
    purpose = data.get('PURPOSE', 'transaction')

    if not user_id or not code:
        return {"status":"error","message":"USER_ID and CODE required","status_code":400}

    ok, msg = verify_otp_util(user_id, code, purpose=purpose)
    if not ok:
        return {"status":"error","message": msg,"status_code":400}

    return {"status":"success","message":"otp verified"}
