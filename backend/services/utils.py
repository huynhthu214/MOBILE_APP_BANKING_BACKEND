# auth/utils.py
import bcrypt
import jwt
import datetime
import random
import uuid
from db import get_conn
from config import JWT_SECRET, JWT_ALGORITHM, ACCESS_EXPIRE_MIN, REFRESH_EXPIRE_DAYS

# ----- password -----
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

# ----- tokens -----
def create_access_token(user_id, role=None):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(minutes=ACCESS_EXPIRE_MIN)
    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # pyjwt returns str in v2
    return token

def create_refresh_token(user_id):
    now = datetime.datetime.utcnow()
    exp = now + datetime.timedelta(days=REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "refresh"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, exp

# ----- refresh store / revoke / blacklist -----
def store_refresh_token(user_id, token, expires_at):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO REFRESH_TOKENS (USER_ID, TOKEN, CREATED_AT, EXPIRES_AT, REVOKED) VALUES (%s,%s,NOW(),%s,0)",
                (user_id, token, expires_at)
            )
        conn.commit()
    finally:
        conn.close()

def revoke_refresh_token(token):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE REFRESH_TOKENS SET REVOKED=1 WHERE TOKEN=%s", (token,))
        conn.commit()
    finally:
        conn.close()

def blacklist_access_token(token):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO TOKEN_BLACKLIST (TOKEN, BLACKLISTED_AT) VALUES (%s, NOW())", (token,))
        conn.commit()
    finally:
        conn.close()

def is_blacklisted(token):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ID FROM TOKEN_BLACKLIST WHERE TOKEN=%s LIMIT 1", (token,))
            return cur.fetchone() is not None
    finally:
        conn.close()

# ----- OTP helpers (OTP_ID kept as varchar per your schema) -----
def generate_otp_code(length=6):
    digits = ''.join(str(random.randint(0,9)) for _ in range(length))
    return digits

def gen_otp_id():
    # generate 10-char hex id, fits varchar(10)
    return uuid.uuid4().hex[:10]

def create_otp(user_id, purpose='transaction', ttl_seconds=300):
    code = generate_otp_code()
    otp_id = gen_otp_id()
    now = datetime.datetime.utcnow()
    expires = now + datetime.timedelta(seconds=ttl_seconds)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO OTP (OTP_ID, USER_ID, CODE, PURPOSE, CREATED_AT, EXPIRES_AT, IS_USED)
                VALUES (%s,%s,%s,%s,%s,%s,0)
            """, (otp_id, user_id, code, purpose, now, expires))
        conn.commit()
    finally:
        conn.close()
    # in dev return code; in prod send SMS/email and DO NOT return
    return otp_id, code

def verify_otp(user_id, code, purpose='transaction'):
    now = datetime.datetime.utcnow()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM OTP
                WHERE USER_ID=%s AND CODE=%s AND PURPOSE=%s AND IS_USED=0
                ORDER BY CREATED_AT DESC LIMIT 1
            """, (user_id, code, purpose))
            row = cur.fetchone()
            if not row:
                return False, "not_found"
            # EXPIRES_AT in your schema might be string or datetime; we assume datetime
            if row.get('EXPIRES_AT') and row['EXPIRES_AT'] < now:
                return False, "expired"
            # mark used
            cur.execute("UPDATE OTP SET IS_USED=1 WHERE OTP_ID=%s", (row['OTP_ID'],))
        conn.commit()
        return True, "ok"
    finally:
        conn.close()
