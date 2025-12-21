from db import get_conn
import datetime

def generate_ekyc_id():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT EKYC_ID FROM EKYC ORDER BY EKYC_ID DESC LIMIT 1")
            last = cur.fetchone()
            if last and last["EKYC_ID"]:
                last_id = last["EKYC_ID"]  
                num = int(last_id[2:]) + 1  
                return f"E{num:03d}"
            return "E001"
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
                (EKYC_ID, USER_ID, IMG_FRONT_URL, IMG_BACK_URL,
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

def get_pending_ekyc():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT 
                    E.EKYC_ID, 
                    E.USER_ID,  
                    E.STATUS, 
                    E.CREATED_AT,
                    U.FULL_NAME,  
                    U.EMAIL     
                FROM EKYC E
                JOIN USER U ON E.USER_ID = U.USER_ID
                WHERE E.STATUS = 'pending'""")
            return cur.fetchall()
    finally:
        conn.close()
        
def update_ekyc_images(user_id, front, back, selfie):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE EKYC
                SET 
                    IMG_FRONT_URL=%s,
                    IMG_BACK_URL=%s,
                    SELFIE_URL=%s,
                    STATUS='pending',
                    REVIEWED_AT=NULL,
                    REVIEWED_BY=NULL
                WHERE USER_ID=%s AND STATUS='rejected'
            """, (front, back, selfie, user_id))
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()
    
def activate_user_after_ekyc(user_id, ekyc_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE USER
                SET EKYC_ID=%s,
                    IS_ACTIVE=true
                WHERE USER_ID=%s
            """, (ekyc_id, user_id))
            conn.commit()
    finally:
        conn.close()

def get_ekyc_by_id(ekyc_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    E.*,
                    U.FULL_NAME,
                    U.EMAIL,
                    U.PHONE
                FROM EKYC E
                JOIN USER U ON E.USER_ID = U.USER_ID
                WHERE E.EKYC_ID = %s
            """, (ekyc_id,))
            return cur.fetchone()
    finally:
        conn.close()