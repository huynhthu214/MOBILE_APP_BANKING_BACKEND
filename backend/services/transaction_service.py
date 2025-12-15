from db import get_conn
from models.transaction_model import *
from models.account_model import *
from models.otp_model import *

# =========================
# EXCEPTION
# =========================
class BusinessException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# =========================
# CREATE
# =========================
def create_deposit(user_id, account_id, amount):
    if amount <= 0:
        raise BusinessException("Invalid amount")

    conn = get_conn()
    try:
        conn.start_transaction()
        tx_id = generate_transaction_id()

        create_transaction(
            conn, tx_id, user_id,
            None, account_id,
            amount, "DEPOSIT", "PENDING"
        )

        create_otp(conn, user_id, tx_id, "DEPOSIT_CONFIRM")
        conn.commit()
        return tx_id
    except:
        conn.rollback()
        raise

def create_withdraw(user_id, account_id, amount):
    conn = get_conn()
    try:
        conn.start_transaction()

        acc = get_account_by_id(conn, account_id, for_update=True)
        if not acc or acc["balance"] < amount:
            raise BusinessException("Insufficient balance")

        tx_id = generate_transaction_id()

        create_transaction(
            conn, tx_id, user_id,
            account_id, None,
            amount, "WITHDRAW", "PENDING"
        )

        create_otp(conn, user_id, tx_id, "WITHDRAW_CONFIRM")
        conn.commit()
        return tx_id
    except:
        conn.rollback()
        raise

def create_transfer(user_id, src_acc, dst_acc, amount):
    conn = get_conn()
    try:
        conn.start_transaction()

        src = get_account_by_id(conn, src_acc, for_update=True)
        dst = get_account_by_id(conn, dst_acc, for_update=True)

        if not src or not dst:
            raise BusinessException("Account not found")
        if src["balance"] < amount:
            raise BusinessException("Insufficient balance")

        tx_id = generate_transaction_id()

        create_transaction(
            conn, tx_id, user_id,
            src_acc, dst_acc,
            amount, "TRANSFER", "PENDING"
        )

        create_otp(conn, user_id, tx_id, "TRANSFER_CONFIRM")
        conn.commit()
        return tx_id
    except:
        conn.rollback()
        raise

# =========================
# CONFIRM
# =========================
def confirm_transaction(user_id, tx_id, otp_code):
    conn = get_conn()
    try:
        conn.start_transaction()

        tx = get_transaction_by_id(conn, tx_id, for_update=True)
        if not tx or tx["status"] != "PENDING":
            raise BusinessException("Invalid transaction")

        verify_otp(conn, user_id, tx_id, otp_code)

        if tx["transaction_type"] == "DEPOSIT":
            update_account_balance(conn, tx["destination_account_id"], tx["amount"])
        elif tx["transaction_type"] == "WITHDRAW":
            update_account_balance(conn, tx["source_account_id"], -tx["amount"])
        elif tx["transaction_type"] == "TRANSFER":
            update_account_balance(conn, tx["source_account_id"], -tx["amount"])
            update_account_balance(conn, tx["destination_account_id"], tx["amount"])

        update_transaction_status(conn, tx_id, "COMPLETED")
        invalidate_otp(conn, tx_id)
        conn.commit()
    except:
        conn.rollback()
        raise

# =========================
# CANCEL / RETRY / ROLLBACK
# =========================
def cancel_pending_transaction(user_id, tx_id):
    conn = get_conn()
    try:
        conn.start_transaction()
        tx = get_transaction_by_id(conn, tx_id, for_update=True)

        if not tx or tx["user_id"] != user_id or tx["status"] != "PENDING":
            raise BusinessException("Cannot cancel")

        cancel_transaction(conn, tx_id)
        invalidate_otp(conn, tx_id)
        conn.commit()
    except:
        conn.rollback()
        raise

def retry_transaction(user_id, tx_id):
    conn = get_conn()
    try:
        conn.start_transaction()
        tx = get_transaction_by_id(conn, tx_id, for_update=True)

        if tx["status"] not in ("FAILED", "TIMEOUT"):
            raise BusinessException("Retry not allowed")

        update_transaction_status(conn, tx_id, "PENDING")
        create_otp(conn, user_id, tx_id, "RETRY_CONFIRM")
        conn.commit()
    except:
        conn.rollback()
        raise

def rollback_transaction(admin_id, tx_id):
    conn = get_conn()
    try:
        conn.start_transaction()
        tx = get_transaction_by_id(conn, tx_id, for_update=True)

        if tx["status"] != "COMPLETED":
            raise BusinessException("Rollback only completed tx")

        if tx["transaction_type"] == "TRANSFER":
            update_account_balance(conn, tx["source_account_id"], tx["amount"])
            update_account_balance(conn, tx["destination_account_id"], -tx["amount"])
        elif tx["transaction_type"] == "DEPOSIT":
            update_account_balance(conn, tx["destination_account_id"], -tx["amount"])
        elif tx["transaction_type"] == "WITHDRAW":
            update_account_balance(conn, tx["source_account_id"], tx["amount"])

        update_transaction_status(conn, tx_id, "ROLLED_BACK")
        conn.commit()
    except:
        conn.rollback()
        raise
