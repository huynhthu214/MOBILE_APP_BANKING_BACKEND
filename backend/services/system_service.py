from db import get_conn
from datetime import datetime


def seed_system():
    conn = get_conn()
    cursor = conn.cursor()

    try:
        # USER ADMIN
        cursor.execute("""
            INSERT INTO USER (USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, CREATED_AT, IS_ACTIVE, PASSWORD_HASH)
            VALUES ('U001', 'Admin', 'admin@gmail.com', '0900000000', 'admin', NOW(), 1, '123456')
        """)

        # USER CLIENT
        cursor.execute("""
            INSERT INTO USER (USER_ID, FULL_NAME, EMAIL, PHONE, ROLE, CREATED_AT, IS_ACTIVE, PASSWORD_HASH)
            VALUES ('U002', 'Client Test', 'client@gmail.com', '0911111111', 'user', NOW(), 1, '123456')
        """)

        # BRANCH
        cursor.execute("""
            INSERT INTO LOCATION (BRANCH_ID, NAME, ADDRESS, LAT, LNG, OPEN_HOURS, CREATED_AT)
            VALUES ('LOC01', 'Chi nhánh trung tâm', 'Q1 - TP.HCM', 10.77, 106.69, '08:00-17:00', NOW())
        """)

        # ACCOUNT
        cursor.execute("""
            INSERT INTO ACCOUNT 
            (ACCOUNT_ID, USER_ID, ACCOUNT_TYPE, BALANCE, INTEREST_RATE, CREATED_AT, STATUS, ACCOUNT_NUMBER)
            VALUES ('A001', 'U002', 'saving', 1000000, 5.5, NOW(), 'active', '0000000001')
        """)

        conn.commit()
        return {"message": "seed_success"}

    except Exception as e:
        return {"message": "seed_failed", "error": str(e)}

    finally:
        cursor.close()
        conn.close()
