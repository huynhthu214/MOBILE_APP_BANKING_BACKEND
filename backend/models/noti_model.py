# models/noti_model.py
from db import get_conn
import pymysql

def get_notifications_by_user_id_model(user_id):
    conn = get_conn()
    try:
        # Sử dụng DictCursor để kết quả trả về là Dictionary {key: value} thay vì Tuple
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            sql = """
                SELECT * FROM NOTIFICATION 
                WHERE USER_ID = %s 
                ORDER BY CREATED_AT DESC
            """
            cur.execute(sql, (user_id,))
            result = cur.fetchall()
            return result
    except Exception as e:
        print(f"Error in noti_model: {e}")
        return []
    finally:
        conn.close()

def mark_all_as_read_model(user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            sql = "UPDATE NOTIFICATION SET IS_READ = 1 WHERE USER_ID = %s"
            cur.execute(sql, (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in mark_all_as_read: {e}")
        return False
    finally:
        conn.close()