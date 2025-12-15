# from db import get_conn

# # ================================
# # Generate ID helper
# # ================================
# def get_last_id(prefix, table, column):
#     conn = get_conn()
#     try:
#         with conn.cursor() as cur:
#             cur.execute(
#                 f"SELECT {column} FROM {table} WHERE {column} LIKE %s ORDER BY {column} DESC LIMIT 1",
#                 (f"{prefix}%",)
#             )
#             row = cur.fetchone()
#             return row[0] if row else None
#     finally:
#         conn.close()


# # ================================
# # Create utility payment
# # ================================
# def create_utility_payment(data):
#     conn = get_conn()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 INSERT INTO UTILITY_PAYMENT 
#                 (UTILITY_PAYMENT_ID, TRANSACTION_ID, PROVIDER_CODE, REFERENCE_CODE_1, REFERENCE_CODE_2, CREATED_AT)
#                 VALUES (%s, %s, %s, %s, %s, NOW())
#             """, (
#                 data["utility_payment_id"],
#                 data["transaction_id"],
#                 data["provider_code"],
#                 data["ref1"],
#                 data["ref2"]
#             ))
#             conn.commit()
#     finally:
#         conn.close()


# # ================================
# # Get utility payment detail
# # ================================
# def get_utility_payment_by_id(payment_id):
#     conn = get_conn()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT up.*, t.AMOUNT, t.STATUS AS TRANSACTION_STATUS
#                 FROM UTILITY_PAYMENT up
#                 JOIN `TRANSACTION` t ON t.TRANSACTION_ID = up.TRANSACTION_ID
#                 WHERE up.UTILITY_PAYMENT_ID = %s
#             """, (payment_id,))

#             row = cur.fetchone()
#             if not row:
#                 return None

#             columns = [col[0] for col in cur.description]
#             return dict(zip(columns, row))
#     finally:
#         conn.close()


# # ================================
# # List all utility payments
# # ================================
# def list_utility_payments():
#     conn = get_conn()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT up.*, t.AMOUNT
#                 FROM UTILITY_PAYMENT up
#                 JOIN `TRANSACTION` t ON t.TRANSACTION_ID = up.TRANSACTION_ID
#                 ORDER BY up.CREATED_AT DESC
#             """)

#             rows = cur.fetchall()
#             if not rows:
#                 return []

#             columns = [col[0] for col in cur.description]
#             return [dict(zip(columns, row)) for row in rows]
#     finally:
#         conn.close()
