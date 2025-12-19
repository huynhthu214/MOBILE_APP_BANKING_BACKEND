from datetime import datetime
from db import get_conn
from services.transaction_service import (
    generate_sequential_id,
    insert_transaction,
    create_otp_conn,
    get_valid_otp_conn,
    mark_otp_used_conn,
    update_account_balance,
    update_transaction_status_conn
)

def now():
    return datetime.now()

# =========================
# CREATE BILL
# =========================
def create_bill_service(user_id, bill_type, amount, due_date, ref=None):
    conn = get_conn()
    try:
        bill_id = generate_sequential_id("B", "BILL", "BILL_ID", conn=conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO BILL
                (BILL_ID, USER_ID, BILL_TYPE, AMOUNT, DUE_DATE, STATUS, REFERENCE)
                VALUES (%s,%s,%s,%s,%s,'UNPAID',%s)
            """, (bill_id, user_id, bill_type, amount, due_date, ref))
        conn.commit()
        return {"status": "success", "bill_id": bill_id}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def get_bill_service(bill_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM BILL WHERE BILL_ID=%s", (bill_id,))
            bill = cur.fetchone()
        if not bill:
            return {"status": "error", "message": "Bill not found"}
        return {"status": "success", "data": bill}
    finally:
        conn.close()


def list_bills_service(user_id=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if user_id:
                cur.execute("SELECT * FROM BILL WHERE USER_ID=%s", (user_id,))
            else:
                cur.execute("SELECT * FROM BILL")
            rows = cur.fetchall()
        return {"status": "success", "data": rows}
    finally:
        conn.close()


# =========================
# PAY BILL – STEP 1
# =========================
def bill_pay_create_service(bill_id, account_id):
    conn = get_conn()
    try:
        conn.begin()

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM BILL WHERE BILL_ID=%s FOR UPDATE", (bill_id,))
            bill = cur.fetchone()

        if not bill or bill["STATUS"] != "UNPAID":
            conn.rollback()
            return {"status": "error", "message": "Invalid bill"}

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID=%s FOR UPDATE", (account_id,))
            acc = cur.fetchone()

        if acc["BALANCE"] < bill["AMOUNT"]:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID", conn=conn)

        tx = {
            "TRANSACTION_ID": tx_id,
            "PAYMENT_ID": bill_id,
            "ACCOUNT_ID": account_id,
            "AMOUNT": bill["AMOUNT"],
            "CURRENCY": "VND",
            "ACCOUNT_TYPE": acc["ACCOUNT_TYPE"],
            "STATUS": "PENDING",
            "CREATED_AT": now(),
            "COMPLETE_AT": None,
            "DEST_ACC_NUM": bill_id,
            "DEST_ACC_NAME": bill["BILL_TYPE"],
            "DEST_BANK_CODE": "BILL",
            "TYPE": "bill"
        }
        insert_transaction(conn, tx)

        otp = create_otp_conn(conn, acc["USER_ID"], "bill")
        print(f"[DEBUG] Send OTP {otp['CODE']}")

        conn.commit()
        return {"status": "success", "transaction_id": tx_id}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


# =========================
# PAY BILL – STEP 2
# =========================
def bill_pay_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM TRANSACTION WHERE TRANSACTION_ID=%s FOR UPDATE", (transaction_id,))
            tx = cur.fetchone()

        if not tx or tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Invalid transaction"}

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID=%s FOR UPDATE", (tx["ACCOUNT_ID"],))
            acc = cur.fetchone()

        otp = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "bill")
        if not otp:
            conn.rollback()
            return {"status": "error", "message": "Invalid OTP"}

        mark_otp_used_conn(conn, otp["OTP_ID"])
        update_account_balance(conn, acc["ACCOUNT_ID"], acc["BALANCE"] - tx["AMOUNT"])
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", now())

        with conn.cursor() as cur:
            cur.execute("UPDATE BILL SET STATUS='PAID' WHERE BILL_ID=%s", (tx["PAYMENT_ID"],))

        conn.commit()
        return {"status": "success", "message": "Bill paid"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()
