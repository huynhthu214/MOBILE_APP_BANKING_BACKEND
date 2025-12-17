from datetime import datetime
from db import get_conn
from services.transaction_service import (
    generate_sequential_id,
    insert_transaction,
    create_otp_conn,
    get_valid_otp_conn,
    mark_otp_used_conn,
    update_transaction_status_conn
)

# =========================
def now():
    return datetime.now()

# =========================
# CREATE UTILITY PAYMENT (STEP 1)
# =========================
def utility_topup_create_service(account_id, provider, phone_number, amount):
    data = {
        "account_id": account_id,
        "provider_code": provider,
        "reference_1": phone_number,
        "amount": amount
    }
    account_id = data.get("account_id")
    provider_code = data.get("provider_code")
    amount = data.get("amount")
    ref1 = data.get("reference_1")
    ref2 = None

    if not all([account_id, provider_code, amount, ref1]):
        return {"status": "error", "message": "Missing required fields"}

    conn = get_conn()
    try:
        conn.begin()

        # lock account
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID=%s FOR UPDATE", (account_id,))
            acc = cur.fetchone()

        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        if acc["BALANCE"] < amount:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        # create transaction
        tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID", conn=conn)

        tx = {
            "TRANSACTION_ID": tx_id,
            "PAYMENT_ID": None,
            "ACCOUNT_ID": account_id,
            "AMOUNT": amount,
            "CURRENCY": "VND",
            "ACCOUNT_TYPE": acc["ACCOUNT_TYPE"],
            "STATUS": "PENDING",
            "CREATED_AT": now(),
            "COMPLETE_AT": None,
            "DEST_ACC_NUM": provider_code,
            "DEST_ACC_NAME": None,
            "DEST_BANK_CODE": "UTILITY",
            "TYPE": "utility"
        }
        insert_transaction(conn, tx)

        # create utility record (pending)
        utility_id = generate_sequential_id("UP", "UTILITY_PAYMENT", "UTILITY_PAYMENT_ID", conn=conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO UTILITY_PAYMENT
                (UTILITY_PAYMENT_ID, TRANSACTION_ID, PROVIDER_CODE, REF1, REF2, CREATED_AT)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (utility_id, tx_id, provider_code, ref1, ref2, now()))

        # OTP
        otp = create_otp_conn(conn, acc["USER_ID"], "utility")
        with conn.cursor() as cur:
            cur.execute("SELECT PHONE FROM USER WHERE USER_ID=%s", (acc["USER_ID"],))
            phone = cur.fetchone()["PHONE"]

        print(f"[DEBUG] Send OTP {otp['CODE']} to {phone} (utility)")

        conn.commit()
        return {
            "status": "success",
            "transaction_id": tx_id,
            "utility_payment_id": utility_id,
            "message": "Utility payment created, waiting OTP"
        }

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


# =========================
# GET DETAIL
# =========================
def get_utility_payment_service(payment_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM UTILITY_PAYMENT WHERE UTILITY_PAYMENT_ID=%s", (payment_id,))
            row = cur.fetchone()
        if not row:
            return {"status": "error", "message": "Not found"}
        return {"status": "success", "data": row}
    finally:
        conn.close()


# =========================
# LIST
# =========================
def list_utility_payment_service():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM UTILITY_PAYMENT ORDER BY CREATED_AT DESC")
            rows = cur.fetchall()
        return {"status": "success", "data": rows}
    finally:
        conn.close()
        
def utility_topup_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM TRANSACTION WHERE TRANSACTION_ID=%s FOR UPDATE",
                (transaction_id,)
            )
            tx = cur.fetchone()

        if not tx or tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Invalid transaction"}

        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM ACCOUNT WHERE ACCOUNT_ID=%s FOR UPDATE",
                (tx["ACCOUNT_ID"],)
            )
            acc = cur.fetchone()

        otp = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "utility")
        if not otp:
            conn.rollback()
            return {"status": "error", "message": "Invalid OTP"}

        mark_otp_used_conn(conn, otp["OTP_ID"])
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", now())

        conn.commit()
        return {"status": "success", "message": "Utility payment completed"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

