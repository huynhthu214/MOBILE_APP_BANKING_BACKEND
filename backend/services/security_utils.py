import jwt
import datetime
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
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(minutes=ACCESS_EXPIRE_MIN)

    print("ACCESS_EXPIRE_MIN =", ACCESS_EXPIRE_MIN)
    print("IAT =", now)
    print("EXP =", exp)

    payload = {
        "sub": user_id,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access"
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(user_id):
    now = datetime.datetime.now()
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
                """
                INSERT INTO REFRESH_TOKEN
                (USER_ID, TOKEN, CREATED_AT, EXPIRES_AT, REVOKED) 
                VALUES (%s,%s,NOW(),%s,0)
                """,
                (user_id, token, expires_at)
            )
        conn.commit()
    finally:
        conn.close()


def revoke_refresh_token(token):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE REFRESH_TOKEN SET REVOKED=1 WHERE TOKEN=%s",
                (token,)
            )
        conn.commit()
    finally:
        conn.close()


def blacklist_access_token(token):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO TOKEN_BLACKLIST (TOKEN, BLACKLISTED_AT) VALUES (%s, NOW())",
                (token,)
            )
        conn.commit()
    finally:
        conn.close()


def is_blacklisted(token):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ID FROM TOKEN_BLACKLIST WHERE TOKEN=%s LIMIT 1",
                (token,)
            )
            return cur.fetchone() is not None
    finally:
        conn.close()


def decode_access_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != "access":
            return None, "Invalid token type"

        if is_blacklisted(token):
            return None, "Token is blacklisted"

        print("Decoded payload:", payload)
        print("Server now:", datetime.datetime.now())

        return payload, None

    except jwt.ExpiredSignatureError:
        return None, "Token expired"
    except Exception:
        return None, "Invalid token"
