# backend/utils.py
from db import get_conn

def generate_sequential_id(table_name, prefix, id_column):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {id_column} FROM {table_name} WHERE {id_column} LIKE %s ORDER BY {id_column} DESC LIMIT 1",
                (f"{prefix}%",)
            )
            last = cur.fetchone()
            
            # Kiểm tra kết quả trả về là Dict hay Tuple
            if last:
                if isinstance(last, dict):
                    last_id = last[id_column]
                else:
                    last_id = last[0] # Giả sử cột ID là cột đầu tiên
                
                num = int(last_id.replace(prefix, ""))
                new_num = num + 1
            else:
                new_num = 1
            return f"{prefix}{new_num:03d}"
    finally:
        conn.close()