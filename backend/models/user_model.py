# backend/models/user_model.py
from db import get_conn

def create_user(data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO USER (USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, PASSWORD_HASH, IS_ACTIVE)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["USER_ID"],
                data["FULL_NAME"],
                data["EMAIL"],
                data.get("PHONE"),
                data.get("ROLE", "user"),
                data["PASSWORD_HASH"],
                1
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


def update_user(user_id, data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE USER 
                SET FULL_NAME=%s, PHONE=%s, ROLE=%s, IS_ACTIVE=%s
                WHERE USER_ID=%s
            """, (
                data["FULL_NAME"],
                data.get("PHONE"),
                data.get("ROLE"),
                data.get("IS_ACTIVE", 1),
                user_id
            ))
            conn.commit()
    finally:
        conn.close()


def search_users(keyword=""):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM USER
                WHERE FULL_NAME LIKE %s OR EMAIL LIKE %s
                ORDER BY CREATED_AT DESC
            """, (f"%{keyword}%", f"%{keyword}%"))
            return cur.fetchall()
    finally:
        conn.close()
