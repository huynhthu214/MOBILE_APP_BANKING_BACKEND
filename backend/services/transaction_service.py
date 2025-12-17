from db import get_conn
from models.transaction_model import (
    get_account_by_number
)
from datetime import datetime, timedelta
import random
import string

def now():
    return datetime.now()

def generate_sequential_id(prefix, table_name, id_col, width=6, conn=None):
    """
    Generate sequential id like T000001 by reading latest id in table.
    If 'conn' is provided, we perform SELECT ... FOR UPDATE inside that transaction
    to avoid race conditions (recommended for TRANSACTION ids).
    """
    close_conn = False
    if conn is None:
        conn = get_conn()
        close_conn = True

    try:
        with conn.cursor() as cur:
            # If we are inside a transaction, use FOR UPDATE to lock the selected row.
            # Use a simple query ordering by id desc; assumes zero-padded numeric part.
            query = f"SELECT {id_col} FROM {table_name} ORDER BY {id_col} DESC LIMIT 1"
            try:
                # If conn is part of a transaction and DB engine supports row-level locks,
                # appending FOR UPDATE will lock the selected row. Only do FOR UPDATE when conn is in a transaction.
                # We'll attempt FOR UPDATE — if DB complains, it's okay fallback to no FOR UPDATE.
                cur.execute(query + " FOR UPDATE")
            except Exception:
                cur.execute(query)

            row = cur.fetchone()
            # row may be None, tuple, or dict-like. Try to extract string id robustly.
            last_id = None
            if not row:
                last_id = None
            else:
                # If row is dict-like
                try:
                    if isinstance(row, dict):
                        last_id = list(row.values())[0]
                    else:
                        # tuple-like -> row[0]
                        last_id = row[0]
                except Exception:
                    last_id = None

            if last_id:
                # remove prefix (e.g. 'T') and parse numeric part
                num_part = last_id.replace(prefix, "")
                try:
                    number = int(num_part)
                except Exception:
                    number = 0
                number += 1
            else:
                number = 1

            return f"{prefix}{number:0{width}d}"
    finally:
        if close_conn:
            conn.close()

def generate_otp_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Stub for sending OTP — integrate real SMS/Email provider here
def send_otp_to_user(user_phone, code, purpose="transaction"):
    # TODO: integrate with SMS gateway or email
    print(f"[DEBUG] Sending OTP {code} to {user_phone} for {purpose}")
    return True

# -------------------------
# DB Access helpers
# -------------------------

def get_account_by_id(conn, account_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s", (account_id,))
        return cur.fetchone()

def get_account_by_number(conn, account_number):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_NUMBER = %s", (account_number,))
        return cur.fetchone()

def update_account_balance(conn, account_id, new_balance):
    with conn.cursor() as cur:
        cur.execute("UPDATE ACCOUNT SET BALANCE = %s WHERE ACCOUNT_ID = %s", (new_balance, account_id))

def insert_transaction(conn, tx):
    cols = ", ".join(tx.keys())
    placeholders = ", ".join(["%s"] * len(tx))
    vals = list(tx.values())
    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO TRANSACTION ({cols}) VALUES ({placeholders})", vals)

def get_transaction_by_id_conn(conn, transaction_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM TRANSACTION WHERE TRANSACTION_ID = %s", (transaction_id,))
        return cur.fetchone()

def update_transaction_status_conn(conn, transaction_id, status, complete_at=None):
    with conn.cursor() as cur:
        if complete_at:
            cur.execute("UPDATE TRANSACTION SET STATUS = %s, COMPLETE_AT = %s WHERE TRANSACTION_ID = %s",
                        (status, complete_at, transaction_id))
        else:
            cur.execute("UPDATE TRANSACTION SET STATUS = %s WHERE TRANSACTION_ID = %s",
                        (status, transaction_id))

# OTP helpers
def create_otp_conn(conn, user_id, purpose, expiry_seconds=300):
    otp_id = generate_sequential_id("O", "OTP", "OTP_ID", width=6, conn=None)  # it's okay to create OTP with separate conn
    code = generate_otp_code()
    created = now()
    expires = created + timedelta(seconds=expiry_seconds)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO OTP (OTP_ID, USER_ID, CODE, PURPOSE, CREATED_AT, EXPIRES_AT, IS_USED) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (otp_id, user_id, code, purpose, created, expires, False)
        )
    return {"OTP_ID": otp_id, "CODE": code, "EXPIRES_AT": expires}

def get_valid_otp_conn(conn, user_id, code, purpose):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM OTP WHERE USER_ID = %s AND CODE = %s AND PURPOSE = %s AND IS_USED = %s AND EXPIRES_AT >= %s",
            (user_id, code, purpose, False, now())
        )
        return cur.fetchone()

def mark_otp_used_conn(conn, otp_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE OTP SET IS_USED = %s WHERE OTP_ID = %s", (True, otp_id))

# -------------------------
# Public services (API handlers)
# -------------------------

# 1) List transactions (global search / admin)
def list_transactions_service(keyword="", page=1, size=50):
    offset = (page - 1) * size
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                kw = f"%{keyword}%"
                cur.execute(
                    """SELECT * FROM TRANSACTION
                       WHERE TRANSACTION_ID LIKE %s
                          OR ACCOUNT_ID LIKE %s
                          OR DEST_ACC_NUM LIKE %s
                          OR DEST_ACC_NAME LIKE %s
                       ORDER BY CREATED_AT DESC
                       LIMIT %s OFFSET %s""",
                    (kw, kw, kw, kw, size, offset)
                )
            else:
                cur.execute(
                    "SELECT * FROM TRANSACTION ORDER BY CREATED_AT DESC LIMIT %s OFFSET %s",
                    (size, offset)
                )
            rows = cur.fetchall()
        return {"status": "success", "data": rows}
    finally:
        conn.close()

# 2) Get transaction by id
def get_transaction_service(transaction_id):
    conn = get_conn()
    try:
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            return {"status": "error", "message": "Transaction not found"}
        return {"status": "success", "data": tx}
    finally:
        conn.close()

# 3) Get account transactions (history) with filters
def get_account_transactions_service(account_id, from_dt=None, to_dt=None, page=1, size=30):
    offset = (page - 1) * size
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            query = "SELECT * FROM TRANSACTION WHERE ACCOUNT_ID = %s"
            params = [account_id]
            if from_dt:
                query += " AND CREATED_AT >= %s"
                params.append(from_dt)
            if to_dt:
                query += " AND CREATED_AT <= %s"
                params.append(to_dt)
            query += " ORDER BY CREATED_AT DESC LIMIT %s OFFSET %s"
            params.extend([size, offset])
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
        return {"status": "success", "data": rows}
    finally:
        conn.close()

# -------------------------
# Deposit flow (create -> confirm)
# -------------------------

def deposit_create_service(account_id, amount, currency="VND"):
    if amount is None or amount <= 0:
        return {"status": "error", "message": "Invalid amount"}

    conn = get_conn()
    try:
        conn.begin()
        acc = get_account_by_id(conn, account_id)
        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        # generate tx id inside this transaction and lock
        tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID", conn=conn)

        tx = {
            "TRANSACTION_ID": tx_id,
            "PAYMENT_ID": None,
            "ACCOUNT_ID": account_id,
            "AMOUNT": amount,
            "CURRENCY": currency,
            "ACCOUNT_TYPE": acc.get("ACCOUNT_TYPE"),
            "STATUS": "PENDING",
            "CREATED_AT": now(),
            "COMPLETE_AT": None,
            "DEST_ACC_NUM": None,
            "DEST_ACC_NAME": None,
            "DEST_BANK_CODE": None,
            "TYPE": "deposit"
        }
        insert_transaction(conn, tx)

        # create OTP and send
        otp = create_otp_conn(conn, acc.get("USER_ID"), purpose="deposit")
        # fetch user phone
        with conn.cursor() as cur:
            cur.execute("SELECT PHONE FROM USER WHERE USER_ID = %s", (acc.get("USER_ID"),))
            user_row = cur.fetchone()
            phone = user_row["PHONE"] if user_row else None
        if phone:
            send_otp_to_user(phone, otp["CODE"], purpose="deposit")
        conn.commit()
        return {"status": "success", "transaction_id": tx_id, "message": "Deposit created, awaiting OTP"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

def deposit_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            conn.rollback()
            return {"status": "error", "message": "Transaction not found"}

        if tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Invalid transaction status"}

        account_id = tx["ACCOUNT_ID"]
        acc = get_account_by_id(conn, account_id)
        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        # validate otp
        otp_row = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "deposit")
        if not otp_row:
            conn.rollback()
            return {"status": "error", "message": "Invalid or expired OTP"}

        # mark otp used
        mark_otp_used_conn(conn, otp_row["OTP_ID"])

        # apply deposit: increase balance
        new_balance = (acc["BALANCE"] or 0) + tx["AMOUNT"]
        update_account_balance(conn, account_id, new_balance)

        # update transaction
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        conn.commit()
        return {"status": "success", "message": "Deposit completed"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

# -------------------------
# Withdraw flow (create -> confirm)
# -------------------------

def withdraw_create_service(account_id, amount, currency="VND"):
    if amount is None or amount <= 0:
        return {"status": "error", "message": "Invalid amount"}

    conn = get_conn()
    try:
        conn.begin()
        acc = get_account_by_id(conn, account_id)
        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        # check balance
        if (acc["BALANCE"] or 0) < amount:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        # TODO: EKYC + daily limit checks here

        tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID", conn=conn)
        tx = {
            "TRANSACTION_ID": tx_id,
            "PAYMENT_ID": None,
            "ACCOUNT_ID": account_id,
            "AMOUNT": amount,
            "CURRENCY": currency,
            "ACCOUNT_TYPE": acc.get("ACCOUNT_TYPE"),
            "STATUS": "PENDING",
            "CREATED_AT": now(),
            "COMPLETE_AT": None,
            "DEST_ACC_NUM": None,
            "DEST_ACC_NAME": None,
            "DEST_BANK_CODE": None,
            "TYPE": "withdraw"
        }
        insert_transaction(conn, tx)

        # create OTP and send
        otp = create_otp_conn(conn, acc.get("USER_ID"), purpose="withdraw")
        with conn.cursor() as cur:
            cur.execute("SELECT PHONE FROM USER WHERE USER_ID = %s", (acc.get("USER_ID"),))
            user_row = cur.fetchone()
            phone = user_row["PHONE"] if user_row else None
        if phone:
            send_otp_to_user(phone, otp["CODE"], purpose="withdraw")

        conn.commit()
        return {"status": "success", "transaction_id": tx_id, "message": "Withdraw created, awaiting OTP"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

def withdraw_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            conn.rollback()
            return {"status": "error", "message": "Transaction not found"}

        if tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Invalid transaction status"}

        account_id = tx["ACCOUNT_ID"]

        # Lock account row to avoid double spend
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (account_id,))
            acc = cur.fetchone()

        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        # validate otp
        otp_row = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "withdraw")
        if not otp_row:
            conn.rollback()
            return {"status": "error", "message": "Invalid or expired OTP"}

        # check balance again
        if (acc["BALANCE"] or 0) < tx["AMOUNT"]:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        # mark otp used
        mark_otp_used_conn(conn, otp_row["OTP_ID"])

        # deduct balance
        new_balance = (acc["BALANCE"] or 0) - tx["AMOUNT"]
        update_account_balance(conn, account_id, new_balance)

        # update transaction
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        conn.commit()
        return {"status": "success", "message": "Withdraw completed"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

# -------------------------
# Transfer flow (create -> confirm)
# -------------------------

def transfer_create_service(from_account_id, to_account_number, amount, to_bank_code="LOCAL", currency="VND", note=None):
    if amount is None or amount <= 0:
        return {"status": "error", "message": "Invalid amount"}

    conn = get_conn()
    try:
        conn.begin()
        src = get_account_by_id(conn, from_account_id)
        if not src:
            conn.rollback()
            return {"status": "error", "message": "Source account not found"}

        if (src["BALANCE"] or 0) < amount:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        # Destination account lookup for LOCAL transfers
        dest = None
        dest_name = None
        if to_bank_code == "LOCAL":
            dest = get_account_by_number(conn, to_account_number)
            if not dest:
                conn.rollback()
                return {"status": "error", "message": "Destination account not found"}
            # dest name should be user's FULL_NAME
            with conn.cursor() as cur:
                cur.execute("SELECT FULL_NAME FROM USER WHERE USER_ID = %s", (dest["USER_ID"],))
                u = cur.fetchone()
                dest_name = u["FULL_NAME"] if u else None

        tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID", conn=conn)
        tx = {
            "TRANSACTION_ID": tx_id,
            "PAYMENT_ID": None,
            "ACCOUNT_ID": from_account_id,
            "AMOUNT": amount,
            "CURRENCY": currency,
            "ACCOUNT_TYPE": src.get("ACCOUNT_TYPE"),
            "STATUS": "PENDING",
            "CREATED_AT": now(),
            "COMPLETE_AT": None,
            "DEST_ACC_NUM": to_account_number,
            "DEST_ACC_NAME": dest_name,
            "DEST_BANK_CODE": to_bank_code,
            "TYPE": "transfer"
        }
        insert_transaction(conn, tx)

        # create and send OTP to source user
        otp = create_otp_conn(conn, src.get("USER_ID"), purpose="transfer")
        with conn.cursor() as cur:
            cur.execute("SELECT PHONE FROM USER WHERE USER_ID = %s", (src.get("USER_ID"),))
            user_row = cur.fetchone()
            phone = user_row["PHONE"] if user_row else None
        if phone:
            send_otp_to_user(phone, otp["CODE"], purpose="transfer")

        conn.commit()
        return {"status": "success", "transaction_id": tx_id, "message": "Transfer created, awaiting OTP"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

def transfer_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            conn.rollback()
            return {"status": "error", "message": "Transaction not found"}

        if tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Invalid transaction status"}

        source_account_id = tx["ACCOUNT_ID"]
        dest_acc_num = tx["DEST_ACC_NUM"]
        amount = tx["AMOUNT"]

        # lock source account
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (source_account_id,))
            src = cur.fetchone()
            if not src:
                conn.rollback()
                return {"status": "error", "message": "Source account not found"}

        # validate otp
        otp_row = get_valid_otp_conn(conn, src["USER_ID"], otp_code, "transfer")
        if not otp_row:
            conn.rollback()
            return {"status": "error", "message": "Invalid or expired OTP"}

        # re-check balance
        if (src["BALANCE"] or 0) < amount:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        # find destination account (local)
        dest = None
        if tx["DEST_BANK_CODE"] == "LOCAL":
            dest = get_account_by_number(conn, dest_acc_num)
            if not dest:
                conn.rollback()
                return {"status": "error", "message": "Destination account not found"}

        # mark otp used
        mark_otp_used_conn(conn, otp_row["OTP_ID"])

        # debit source
        new_src_balance = (src["BALANCE"] or 0) - amount
        update_account_balance(conn, source_account_id, new_src_balance)

        # credit destination if local
        if dest:
            # lock dest row to be safe
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (dest["ACCOUNT_ID"],))
                dest_locked = cur.fetchone()
            new_dest_balance = (dest_locked["BALANCE"] or 0) + amount
            update_account_balance(conn, dest_locked["ACCOUNT_ID"], new_dest_balance)

        # update transaction status
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        conn.commit()
        return {"status": "success", "message": "Transfer completed"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

# -------------------------
# Additional utilities
# -------------------------

def resend_otp_service(transaction_id):
    """
    If user requests resend OTP for a pending transaction.
    """
    conn = get_conn()
    try:
        conn.begin()
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            conn.rollback()
            return {"status": "error", "message": "Transaction not found"}

        if tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Transaction not pending"}

        # fetch account and user
        acc = get_account_by_id(conn, tx["ACCOUNT_ID"])
        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        otp = create_otp_conn(conn, acc["USER_ID"], purpose=tx["TYPE"])
        with conn.cursor() as cur:
            cur.execute("SELECT PHONE FROM USER WHERE USER_ID = %s", (acc.get("USER_ID"),))
            user_row = cur.fetchone()
            phone = user_row["PHONE"] if user_row else None
        if phone:
            send_otp_to_user(phone, otp["CODE"], purpose=tx["TYPE"])

        conn.commit()
        return {"status": "success", "message": "OTP resent"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()
