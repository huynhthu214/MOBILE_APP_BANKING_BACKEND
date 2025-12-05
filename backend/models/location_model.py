from db import get_conn

def get_all_locations():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM LOCATION")
            return cur.fetchall()
    finally:
        conn.close()


def get_location_by_id(branch_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM LOCATION WHERE BRANCH_ID=%s",
                (branch_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


def insert_location(data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO LOCATION
                (BRANCH_ID, NAME, ADDRESS, LAT, LNG, OPEN_HOURS, CREATED_AT)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)
            conn.commit()
    finally:
        conn.close()


def update_location(branch_id, data):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE LOCATION SET
                NAME=%s, ADDRESS=%s, LAT=%s, LNG=%s, OPEN_HOURS=%s
                WHERE BRANCH_ID=%s
            """, (*data, branch_id))
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()


def delete_location(branch_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM LOCATION WHERE BRANCH_ID=%s",
                (branch_id,)
            )
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()
