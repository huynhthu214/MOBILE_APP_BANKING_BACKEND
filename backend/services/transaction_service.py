from db import get_conn
from models.transaction_model import (
    get_transactions,
    get_transaction_by_id,
    create_transaction,
    update_transaction_status,
    get_account,
    get_account_by_number,
    update_balance,
    get_valid_otp,
    mark_otp_used,
)

# ============================================================
# ID GENERATOR
# ============================================================
def generate_sequential_id(prefix, table_name, id_col):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {id_col} FROM {table_name} WHERE {id_col} LIKE %s ORDER BY {id_col} DESC LIMIT 1",
                (f"{prefix}%",)
            )
            row = cur.fetchone()

            if row:
                last_num = int(row[id_col].replace(prefix, ""))
                new_num = last_num + 1
            else:
                new_num = 1

            return f"{prefix}{new_num:03d}"
    finally:
        conn.close()


# ============================================================
# LIST TRANSACTIONS
# ============================================================
def list_transactions_service(keyword=""):
    records = get_transactions(keyword)
    return {"status": "success", "data": records}


# ============================================================
# GET
# ============================================================
def get_transaction_service(transaction_id):
    tx = get_transaction_by_id(transaction_id)
    if not tx:
        return {"status": "error", "message": "Transaction not found"}
    return {"status": "success", "data": tx}


# ============================================================
# DEPOSIT
# ============================================================
def deposit_service(account_id, amount):
    acc = get_account(account_id)
    if not acc:
        return {"status": "error", "message": "Account not found"}

    tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID")

    create_transaction({
        "transaction_id": tx_id,
        "payment_id": None,
        "account_id": account_id,
        "amount": amount,
        "type": "deposit",
        "status": "COMPLETED"
    })

    update_balance(account_id, amount, increase=True)

    return {"status": "success", "transaction_id": tx_id}


# ============================================================
# WITHDRAW
# ============================================================
def withdraw_service(account_id, amount):
    acc = get_account(account_id)
    if not acc:
        return {"status": "error", "message": "Account not found"}

    if acc["BALANCE"] < amount:
        return {"status": "error", "message": "Insufficient balance"}

    tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID")

    create_transaction({
        "transaction_id": tx_id,
        "payment_id": None,
        "account_id": account_id,
        "amount": amount,
        "type": "withdraw",
        "status": "COMPLETED"
    })

    update_balance(account_id, amount, increase=False)

    return {"status": "success", "transaction_id": tx_id}


# ============================================================
# TRANSFER (STEP 1 – CREATE)
# ============================================================
def transfer_create_service(from_acc_id, dest_acc_num, amount):
    src_acc = get_account(from_acc_id)
    if not src_acc:
        return {"status": "error", "message": "Source account not found"}

    if src_acc["BALANCE"] < amount:
        return {"status": "error", "message": "Insufficient balance"}

    dest_acc = get_account_by_number(dest_acc_num)
    if not dest_acc:
        return {"status": "error", "message": "Destination account not found"}

    tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID")

    create_transaction({
        "transaction_id": tx_id,
        "payment_id": None,
        "account_id": from_acc_id,
        "amount": amount,
        "status": "PENDING",
        "type": "transfer",
        "dest_acc_num": dest_acc_num,
        "dest_acc_name": dest_acc["ACCOUNT_ID"],
        "dest_bank_code": "LOCAL"
    })

    return {"status": "success", "transaction_id": tx_id, "message": "Transfer created, awaiting OTP"}


# ============================================================
# TRANSFER (STEP 2 – CONFIRM OTP)
# ============================================================
def transfer_confirm_service(transaction_id, otp_code):
    tx = get_transaction_by_id(transaction_id)
    if not tx:
        return {"status": "error", "message": "Transaction not found"}

    src_acc_id = tx["ACCOUNT_ID"]
    amount = tx["AMOUNT"]
    dest_acc_num = tx["DEST_ACC_NUM"]

    # 1. Check OTP
    src_acc = get_account(src_acc_id)
    otp = get_valid_otp(src_acc["USER_ID"], otp_code)

    if not otp:
        return {"status": "error", "message": "Invalid or expired OTP"}

    mark_otp_used(otp["OTP_ID"])

    # 2. Re-check balance
    if src_acc["BALANCE"] < amount:
        return {"status": "error", "message": "Insufficient balance"}

    dest_acc = get_account_by_number(dest_acc_num)
    if not dest_acc:
        return {"status": "error", "message": "Destination account not found"}

    # 3. Update balances
    update_balance(src_acc_id, amount, increase=False)
    update_balance(dest_acc["ACCOUNT_ID"], amount, increase=True)

    # 4. Update transaction
    update_transaction_status(transaction_id, "COMPLETED")

    return {"status": "success", "message": "Transfer completed"}

#phần Minh Thư thêm nè
#Tạo giao dịch nạp
def deposit_create_service(account_id, amount):
    acc = get_account(account_id)
    if not acc:
        return {"status": "error", "message": "Account not found"}

    tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID")

    create_transaction({
        "transaction_id": tx_id,
        "payment_id": None,
        "account_id": account_id,
        "amount": amount,
        "currency": "VND",
        "account_type": acc["ACCOUNT_TYPE"],
        "status": "PENDING",
        "type": "deposit"
    })

    # TODO: gọi hàm gửi OTP
    return {
        "status": "success",
        "transaction_id": tx_id,
        "message": "Deposit created, waiting OTP"
    }

#Xác nhận OTP cho nạp
def deposit_confirm_service(transaction_id, otp_code):
    tx = get_transaction_by_id(transaction_id)
    if not tx or tx["STATUS"] != "PENDING":
        return {"status": "error", "message": "Invalid transaction"}

    acc = get_account(tx["ACCOUNT_ID"])
    otp = get_valid_otp(acc["USER_ID"], otp_code)
    if not otp:
        return {"status": "error", "message": "Invalid or expired OTP"}

    mark_otp_used(otp["OTP_ID"])

    update_balance(acc["ACCOUNT_ID"], tx["AMOUNT"], increase=True)
    update_transaction_status(transaction_id, "COMPLETED")

    return {"status": "success", "message": "Deposit completed"}

#Tạo giao dịch rút 
def withdraw_create_service(account_id, amount):
    acc = get_account(account_id)
    if not acc:
        return {"status": "error", "message": "Account not found"}

    if acc["BALANCE"] < amount:
        return {"status": "error", "message": "Insufficient balance"}

    # TODO: check EKYC + hạn mức tại đây

    tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID")

    create_transaction({
        "transaction_id": tx_id,
        "payment_id": None,
        "account_id": account_id,
        "amount": amount,
        "currency": "VND",
        "account_type": acc["ACCOUNT_TYPE"],
        "status": "PENDING",
        "type": "withdraw"
    })

    # TODO: gửi OTP
    return {
        "status": "success",
        "transaction_id": tx_id,
        "message": "Withdraw created, waiting OTP"
    }
    
#Xác nhận OTP cho rút
def withdraw_confirm_service(transaction_id, otp_code):
    tx = get_transaction_by_id(transaction_id)
    if not tx or tx["STATUS"] != "PENDING":
        return {"status": "error", "message": "Invalid transaction"}

    acc = get_account(tx["ACCOUNT_ID"])

    otp = get_valid_otp(acc["USER_ID"], otp_code)
    if not otp:
        return {"status": "error", "message": "Invalid OTP"}

    mark_otp_used(otp["OTP_ID"])

    if acc["BALANCE"] < tx["AMOUNT"]:
        return {"status": "error", "message": "Insufficient balance"}

    update_balance(acc["ACCOUNT_ID"], tx["AMOUNT"], increase=False)
    update_transaction_status(transaction_id, "COMPLETED")

    return {"status": "success", "message": "Withdraw completed"}

