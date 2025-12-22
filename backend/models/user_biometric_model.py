from db import get_conn
from datetime import datetime
import json

class UserBiometricModel:
    TABLE = "USER_BIOMETRIC"

    @staticmethod
    def register_face(user_id, face_embedding, device_biometric=False):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                biometric_id = f"BIO{int(datetime.now().timestamp())}"
                embedding_str = json.dumps(face_embedding.tolist())  # lưu dạng string
                cur.execute(f"""
                    INSERT INTO {UserBiometricModel.TABLE} 
                    (USER_ID, BIOMETRIC_ID, FACE_TEMPLATE_HASH, DEVICE_BIOMETRIC, FACE_ENABLED, CREATED_AT)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (user_id, biometric_id, embedding_str, device_biometric, True))
                conn.commit()
                return biometric_id
        finally:
            conn.close()

    @staticmethod
    def get_face(user_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT * FROM {UserBiometricModel.TABLE}
                    WHERE USER_ID=%s AND FACE_ENABLED=1
                    ORDER BY CREATED_AT DESC LIMIT 1
                """, (user_id,))
                row = cur.fetchone()
                if row:
                    import json
                    row['FACE_TEMPLATE_HASH'] = json.loads(row['FACE_TEMPLATE_HASH'])
                return row
        finally:
            conn.close()
