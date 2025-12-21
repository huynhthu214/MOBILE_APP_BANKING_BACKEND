from db import get_conn
import pymysql
class DashboardModel:

    @staticmethod
    def get_total_users():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Đếm user có role là USER (bỏ qua ADMIN)
                cur.execute("SELECT COUNT(*) as total FROM USER WHERE ROLE = 'customer'")
                result = cur.fetchone()
                return result['total'] if result else 0
        finally:
            conn.close()

    @staticmethod
    def get_total_transactions():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Đếm giao dịch thành công. LƯU Ý: Tên bảng là TRANSACTION
                cur.execute("SELECT COUNT(*) as total FROM TRANSACTIONS WHERE STATUS = 'COMPLETED'") 
                result = cur.fetchone()
                return result['total'] if result else 0
        finally:
            conn.close()

    @staticmethod
    def get_total_transaction_amount():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                # Tính tổng tiền. LƯU Ý: Tên bảng là TRANSACTION
                cur.execute("SELECT SUM(AMOUNT) as total FROM TRANSACTIONS WHERE STATUS = 'completed'")
                result = cur.fetchone()
                # Nếu không có giao dịch nào, SUM sẽ trả về None -> trả về 0
                return result['total'] if result and result['total'] else 0
        finally:
            conn.close()

    @staticmethod
    def get_recent_transactions(limit=5):
        conn = get_conn()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = """
                    SELECT 
                        TRANSACTION_ID, 
                        AMOUNT, 
                        CREATED_AT,
                        TYPE,
                        STATUS
                    FROM TRANSACTIONS 
                    ORDER BY CREATED_AT DESC 
                    LIMIT %s
                """
                cur.execute(sql, (limit,))
                return cur.fetchall()
        finally:
            conn.close()
        
    @staticmethod
    def get_all_customers(search_query=None):
        conn = get_conn()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                # Chỉ lấy ROLE = 'customer' như bạn yêu cầu
                sql = "SELECT * FROM USER WHERE ROLE = 'customer'"
                params = []
                
                # Logic tìm kiếm theo Tên, Email hoặc SĐT
                if search_query:
                    sql += " AND (FULL_NAME LIKE %s OR EMAIL LIKE %s OR PHONE LIKE %s)"
                    like_query = f"%{search_query}%"
                    params.extend([like_query, like_query, like_query])
                
                sql += " ORDER BY CREATED_AT DESC"
                
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_all_transactions(search_query=None, status_filter=None):
        conn = get_conn()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                # Lưu ý: Tên bảng là TRANSACTIONS (số nhiều)
                sql = "SELECT * FROM TRANSACTIONS WHERE 1=1" 
                params = []

                # Lọc theo trạng thái (Success/Failed) nếu có
                if status_filter and status_filter != 'ALL':
                    sql += " AND STATUS = %s"
                    params.append(status_filter)

                # Logic tìm kiếm theo Mã GD hoặc Tên người nhận
                if search_query:
                    sql += " AND (TRANSACTION_ID LIKE %s OR DEST_ACC_NAME LIKE %s)"
                    like_query = f"%{search_query}%"
                    params.extend([like_query, like_query])

                sql += " ORDER BY CREATED_AT DESC"
                
                cur.execute(sql, params)
                return cur.fetchall()
        finally:
            conn.close()