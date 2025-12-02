# services/payment_service.py
from models.payment_model import (
    get_bills, get_bill_by_id, update_bill_status,
    create_bill_payment, create_transaction,
    get_account, update_account_balance,
    create_utility_payment
)
from db import get_conn
from datetime import datetime

# =============================
# ID GENERATOR (SEQUENTIAL)
# =============================
def generate_sequential_id(table_name, prefix, id_column):

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {id_column} FROM {table_name} WHERE {id_column} LIKE %s ORDER BY {id_column} DESC LIMIT 1",
                (f"{prefix}%",)
            )
            last = cur.fetchone()
            if last:
                last_id = last[id_column]
                num = int(last_id.replace(prefix, ""))
                new_num = num + 1
            else:
                new_num = 1
            return f"{prefix}{new_num:03d}"
    finally:
        conn.close()

# =============================
# BILL SERVICES
# =============================
def list_bills_service(keyword=""):
    try:
        bills = get_bills(keyword)
        return {"status": "success", "data": bills}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_bill_service(bill_id):
    bill = get_bill_by_id(bill_id)
    if bill:
        return {"status": "success", "data": bill}
    else:
        return {"status": "error", "message": "Bill not found", "status_code": 404}

# =============================
# BILL PAYMENT SERVICE
# =============================
def pay_bill_service(account_id, bill_id):
    account = get_account(account_id)
    if not account:
        return {"status": "error", "message": "Account not found"}

    bill = get_bill_by_id(bill_id)
    if not bill:
        return {"status": "error", "message": "Bill not found"}

    # Sửa ở đây
    if bill["STATUS"] == "paid":
        return {"status": "error", "message": "Bill already paid"}

    amount_due = bill["AMOUNT_DUE"]
    if account["BALANCE"] < amount_due:
        return {"status": "error", "message": "Insufficient balance"}

    transaction_id = generate_sequential_id("TRANSACTION", "T", "TRANSACTION_ID")
    create_transaction(transaction_id, account_id, amount_due, "VND", "BILL_PAYMENT")

    payment_id = generate_sequential_id("BILL_PAYMENT", "BP", "PAYMENT_ID")
    create_bill_payment(payment_id, transaction_id, bill_id)

    update_bill_status(bill_id, "paid")
    update_account_balance(account_id, amount_due)

    return {"status": "success", "transaction_id": transaction_id, "payment_id": payment_id}

# =============================
# UTILITY PAYMENT SERVICE
# =============================
def create_utility_payment_service(transaction_id, provider_code, ref1, ref2):
    utility_payment_id = generate_sequential_id("UTILITY_PAYMENT", "UP", "UTILITY_PAYMENT_ID")
    create_utility_payment(utility_payment_id, transaction_id, provider_code, ref1, ref2)
    return {"status": "success", "utility_payment_id": utility_payment_id}
