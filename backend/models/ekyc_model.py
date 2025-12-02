from db import get_conn
import datetime

def generate_ekyc_id():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EKYC_ID FROM EKYC ORDER BY EKYC_ID DESC LIMIT 1")
            last = cur.fetchone()
            if last and last["EKYC_ID"]:
                last_id = last["EKYC_ID"]   # ví dụ: EK002
                num = int(last_id[2:]) + 1  # cắt đúng sau "EK"
                return f"EK{num:03d}"
            return "EK001"
    finally:
        conn.close()


def get_ekyc_by_user(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM EKYC WHERE USER_ID=%s", (user_id,))
            return cur.fetchone()
    finally:
        conn.close()


def insert_ekyc(data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO EKYC
                (EKYC_ID, USER_ID, ID_IMG_FRONT_URL, ID_IMG_BACK_URL,
                 SELFIE_URL, STATUS, REVIEWED_AT, REVIEWED_BY, CREATED_AT)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, data)
            conn.commit()
    finally:
        conn.close()


def update_ekyc_review(user_id, status, reviewed_by):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE EKYC
                SET STATUS=%s,
                    REVIEWED_AT=%s,
                    REVIEWED_BY=%s
                WHERE USER_ID=%s
            """, (status, datetime.datetime.now(), reviewed_by, user_id))
            conn.commit()
    finally:
        conn.close()


def bind_ekyc_to_user(user_id, ekyc_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE USER SET EKYC_ID=%s WHERE USER_ID=%s
            """, (ekyc_id, user_id))
            conn.commit()
    finally:
        conn.close()
