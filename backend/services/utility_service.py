# from datetime import datetime
# from db import get_conn
# from models.utility_payment_model import (
#     create_utility_payment,
#     get_utility_payment_by_id,
#     list_utility_payments
# )
# from models.transaction_model import (
#     create_transaction,
#     # get_account,
#     # update_balance
# )


# # ================================================
# # GENERATE SEQUENTIAL ID (reuse from transaction style)
# # ================================================
# def generate_sequential_id(prefix, table, column):
#     conn = get_conn()
#     cur = conn.cursor()
    
#     cur.execute(
#         f"SELECT {column} FROM {table} WHERE {column} LIKE %s ORDER BY {column} DESC LIMIT 1",
#         (f"{prefix}%",)
#     )

#     row = cur.fetchone()

#     if row and column in row:
#         last_num = int(row[column].replace(prefix, ""))
#         new_num = last_num + 1
#     else:
#         new_num = 1

#     return f"{prefix}{new_num:03d}"


# # ================================================
# # CREATE UTILITY PAYMENT
# # ================================================
# def create_utility_payment_service(data):

#     account_id = data["account_id"]
#     provider_code = data["provider_code"]
#     amount = float(data["amount"])
#     ref1 = data["reference_1"]
#     ref2 = data.get("reference_2", None)

#     # 1. Validate account
#     acc = get_account(account_id)
#     if not acc:
#         return {"status": "error", "message": "Account not found"}

#     if acc["BALANCE"] < amount:
#         return {"status": "error", "message": "Insufficient balance"}

#     # 2. Create transaction entry
#     tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID")

#     create_transaction({
#         "transaction_id": tx_id,
#         "payment_id": None,
#         "account_id": account_id,
#         "amount": amount,
#         "type": "UTILITY_PAYMENT",
#         "status": "COMPLETED",
#         "dest_acc_num": provider_code,
#         "dest_acc_name": None,
#         "dest_bank_code": None
#     })

#     # 3. Create utility payment record
#     utility_id = generate_sequential_id("UP", "UTILITY_PAYMENT", "UTILITY_PAYMENT_ID")

#     create_utility_payment({
#         "utility_payment_id": utility_id,
#         "transaction_id": tx_id,
#         "provider_code": provider_code,
#         "ref1": ref1,
#         "ref2": ref2
#     })

#     # 4. Update balance
#     update_balance(account_id, amount, increase=False)

#     return {
#         "status": "success",
#         "utility_payment_id": utility_id,
#         "transaction_id": tx_id
#     }


# # ================================================
# # GET DETAIL
# # ================================================
# def get_utility_payment_service(payment_id):
#     record = get_utility_payment_by_id(payment_id)
#     if not record:
#         return {"status": "error", "message": "Utility payment not found"}
#     return {"status": "success", "data": record}


# # ================================================
# # LIST
# # ================================================
# def list_utility_payment_service():
#     data = list_utility_payments()
#     return {"status": "success", "data": data}
