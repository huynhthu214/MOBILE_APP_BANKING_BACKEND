from datetime import datetime
import uuid

# =========================
# ID GENERATOR
# =========================
def generate_transaction_id():
    return "T" + uuid.uuid4().hex[:10].upper()

# =========================
# CREATE
# =========================
def create_transaction(
    conn, tx_id, user_id, source_acc, dest_acc,
    amount, tx_type, status, description=None
):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (
            transaction_id, user_id,
            source_account_id, destination_account_id,
            amount, transaction_type,
            status, description, created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        tx_id, user_id,
        source_acc, dest_acc,
        amount, tx_type,
        status, description,
        datetime.utcnow()
    ))

# =========================
# READ
# =========================
def get_transaction_by_id(conn, tx_id, for_update=False):
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM transactions WHERE transaction_id=%s"
    if for_update:
        sql += " FOR UPDATE"
    cursor.execute(sql, (tx_id,))
    return cursor.fetchone()

def get_transactions_by_account(conn, account_id, limit=50, offset=0):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE source_account_id=%s OR destination_account_id=%s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (account_id, account_id, limit, offset))
    return cursor.fetchall()

def get_transactions_by_user(conn, user_id, limit=50, offset=0):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE user_id=%s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (user_id, limit, offset))
    return cursor.fetchall()

# =========================
# UPDATE STATUS
# =========================
def update_transaction_status(conn, tx_id, status):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET status=%s, updated_at=%s
        WHERE transaction_id=%s
    """, (status, datetime.utcnow(), tx_id))

def cancel_transaction(conn, tx_id):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET status='CANCELLED', updated_at=%s
        WHERE transaction_id=%s AND status='PENDING'
    """, (datetime.utcnow(), tx_id))

def get_transactions(account_id, limit=50, offset=0):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT *
        FROM transactions
        WHERE source_account_id = %s
           OR destination_account_id = %s
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, (account_id, account_id, limit, offset))
    return cursor.fetchall()