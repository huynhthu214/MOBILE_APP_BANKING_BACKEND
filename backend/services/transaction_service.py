from db import get_conn
from models.transaction_model import TransactionModel
from datetime import datetime, timedelta
import random
import string

# --- IMPORT SERVICE CỦA BẠN (DÙNG LẠI) ---
from services.mail_service import send_email
from services.mail_templates import otp_email_template

def now():
    return datetime.now()

def generate_sequential_id(prefix, table_name, id_col, width=6, conn=None):
    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT {id_col} FROM {table_name} ORDER BY {id_col} DESC LIMIT 1"
        )
        row = cursor.fetchone()

        if not row:
            return f"{prefix}{str(1).zfill(width)}"

        last_id = row[id_col]   
        last_num = int(last_id[len(prefix):])
        return f"{prefix}{str(last_num + 1).zfill(width)}"

def generate_otp_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_otp_to_user(user_phone, code, purpose="transaction"):
    # TODO: integrate with SMS gateway
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
    # Đảm bảo key khớp với tên cột trong DB
    cols = ", ".join(tx.keys())
    placeholders = ", ".join(["%s"] * len(tx))
    vals = list(tx.values())
    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO TRANSACTIONS ({cols}) VALUES ({placeholders})", vals)

def get_transaction_by_id_conn(conn, transaction_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM TRANSACTIONS WHERE TRANSACTION_ID = %s", (transaction_id,))
        return cur.fetchone()

def update_transaction_status_conn(conn, transaction_id, status, complete_at=None):
    with conn.cursor() as cur:
        if complete_at:
            cur.execute("UPDATE TRANSACTIONS SET STATUS = %s, COMPLETE_AT = %s WHERE TRANSACTION_ID = %s",
                        (status, complete_at, transaction_id))
        else:
            cur.execute("UPDATE TRANSACTIONS SET STATUS = %s WHERE TRANSACTION_ID = %s",
                        (status, transaction_id))

# OTP helpers
def create_otp_conn(conn, user_id, purpose, expiry_seconds=300):
    otp_id = generate_sequential_id("O", "OTP", "OTP_ID", width=6, conn=conn) 
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
    current_time = now()
    print(f"[DEBUG] Checking OTP: User={user_id}, Code={code}, Purpose={purpose}, Time={current_time}")
    with conn.cursor() as cur:
        # Đảm bảo câu lệnh SQL so sánh đúng cột EXPIRES_AT
        cur.execute(
            "SELECT * FROM OTP WHERE USER_ID = %s AND CODE = %s AND PURPOSE = %s AND IS_USED = %s AND EXPIRES_AT >= %s",
            (user_id, code, purpose, False, current_time)
        )
        return cur.fetchone()

def mark_otp_used_conn(conn, otp_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE OTP SET IS_USED = %s WHERE OTP_ID = %s", (True, otp_id))

# -------------------------
# Public services
# -------------------------

# !!! NEW FUNCTION ADDED TO FIX IMPORT ERROR !!!
def create_transaction(tx_data):
    """
    Hàm này được dùng bởi các service khác (ví dụ: account_service.pay_mortgage)
    để tạo giao dịch trực tiếp mà không cần quy trình OTP.
    """
    # Chuẩn hóa key thành chữ hoa để khớp với DB (nếu tx_data truyền vào là chữ thường)
    normalized_tx = {k.upper(): v for k, v in tx_data.items()}
    
    if "CREATED_AT" not in normalized_tx:
        normalized_tx["CREATED_AT"] = now()

    conn = get_conn()
    try:
        insert_transaction(conn, normalized_tx)
        conn.commit()
        return True
    except Exception as e:
        print(f"[create_transaction] Error: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

# 1) List transactions (Global)
def list_transactions_service(keyword="", page=1, size=50, account_id=None):
    conn = get_conn()
    try:
        # Chuyển đổi page/size sang int đề phòng trường hợp truyền vào string
        _page = int(page)
        _size = int(size)
        offset = (_page - 1) * _size
        
        with conn.cursor() as cur:
            # Trường hợp 1: Lọc theo account_id (Lịch sử giao dịch của 1 người)
            if account_id:
                 cur.execute(
                    "SELECT * FROM TRANSACTIONS WHERE ACCOUNT_ID=%s ORDER BY CREATED_AT DESC LIMIT %s OFFSET %s",
                    (account_id, _size, offset)
                )
            
            # Trường hợp 2: Search chung (Admin hoặc tìm kiếm)
            elif keyword:
                kw = f"%{keyword}%"
                cur.execute(
                    """SELECT * FROM TRANSACTIONS
                       WHERE TRANSACTION_ID LIKE %s
                          OR ACCOUNT_ID LIKE %s
                          OR DEST_ACC_NUM LIKE %s
                       ORDER BY CREATED_AT DESC LIMIT %s OFFSET %s""",
                    (kw, kw, kw, _size, offset)
                )
            
            # Trường hợp 3: Lấy tất cả (Mặc định)
            else:
                cur.execute(
                    "SELECT * FROM TRANSACTIONS ORDER BY CREATED_AT DESC LIMIT %s OFFSET %s",
                    (_size, offset)
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

# 3) Get account transactions
def get_account_transactions_service(account_id, from_dt=None, to_dt=None, page=1, size=30):
    return list_transactions_service(page=page, size=size, account_id=account_id)

# -------------------------
# Deposit flow (create -> confirm)
# -------------------------

def deposit_create_service(account_id, amount, currency="VND"):
    if amount is None or amount <= 0:
        return {"status": "error", "message": "Số tiền không hợp lệ"}

    conn = get_conn()
    try:
        conn.begin()
        
        # 1. Kiểm tra tài khoản
        acc = get_account_by_id(conn, account_id)
        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản không tồn tại"}

        # 2. Tạo Transaction ID
        tx_id = generate_sequential_id("T", "TRANSACTIONS", "TRANSACTION_ID", conn=conn)

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

        # 3. Tạo OTP
        user_id = acc.get("USER_ID")
        otp = create_otp_conn(conn, user_id, purpose="deposit")
        
        # 4. Lấy EMAIL từ bảng USER (Query trực tiếp, không qua User Model)
        user_email = None
        with conn.cursor() as cur:
            cur.execute("SELECT EMAIL FROM USER WHERE USER_ID = %s", (user_id,))
            user_row = cur.fetchone()
            if user_row:
                # Xử lý trường hợp DB trả về dict hoặc tuple
                user_email = user_row["EMAIL"] if isinstance(user_row, dict) else user_row[0]

        # 5. Gửi Email OTP
        if user_email:
            html_content = otp_email_template(otp["CODE"], purpose="Giao dịch Nạp tiền")
            is_sent, error_msg = send_email(user_email, "Xác thực Nạp tiền - ZY Banking", html_content)
            
            if not is_sent:
                conn.rollback()
                print(f"[MAIL ERROR] {error_msg}")
                return {"status": "error", "message": "Lỗi gửi email OTP. Vui lòng thử lại sau."}
        else:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản này chưa đăng ký Email."}

        # 6. Thành công
        conn.commit()
        return {
            "status": "success", 
            "transaction_id": tx_id, 
            "message": "Mã OTP đã được gửi tới email của bạn."
        }

    except Exception as e:
        conn.rollback()
        print(f"[SYSTEM ERROR] {e}")
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}
    finally:
        conn.close()

def deposit_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        
        # 1. Lấy thông tin giao dịch
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            conn.rollback()
            return {"status": "error", "message": "Giao dịch không tồn tại"}

        # 2. Kiểm tra trạng thái giao dịch (Chỉ xử lý nếu đang PENDING)
        if tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Giao dịch đã hoàn tất hoặc bị hủy trước đó"}

        account_id = tx["ACCOUNT_ID"]

        # 3. Khóa tài khoản (Locking) để tránh xung đột dữ liệu
        # Dùng FOR UPDATE để đảm bảo không ai sửa tài khoản này khi đang nạp
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (account_id,))
            acc = cur.fetchone()

        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản không tồn tại"}

        # 4. Xác thực OTP
        # Lưu ý: acc["USER_ID"] lấy từ bảng ACCOUNT đã lock
        otp_row = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "deposit")
        
        if not otp_row:
            conn.rollback()
            return {"status": "error", "message": "Mã OTP không đúng hoặc đã hết hạn"}

        # 5. Đánh dấu OTP đã sử dụng
        mark_otp_used_conn(conn, otp_row["OTP_ID"])

        # 6. CẬP NHẬT SỐ DƯ (QUAN TRỌNG)
        # Sử dụng câu lệnh SQL cộng trực tiếp để đảm bảo an toàn tuyệt đối
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE ACCOUNT SET BALANCE = BALANCE + %s WHERE ACCOUNT_ID = %s", 
                (tx["AMOUNT"], account_id)
            )

        # 7. Cập nhật trạng thái giao dịch -> COMPLETED
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        conn.commit()
        return {"status": "success", "message": "Nạp tiền thành công"}

    except Exception as e:
        conn.rollback()
        # Log lỗi ra console để debug
        print(f"[DEPOSIT ERROR] TransactionID: {transaction_id} - Error: {str(e)}")
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}
    finally:
        conn.close()

# -------------------------
# Withdraw flow (create -> confirm)
# -------------------------

def withdraw_create_service(account_id, amount, currency="VND"):
    if amount is None or amount <= 0:
        return {"status": "error", "message": "Số tiền không hợp lệ"}

    conn = get_conn()
    try:
        conn.begin()
        
        # 1. Kiểm tra tài khoản
        acc = get_account_by_id(conn, account_id)
        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản không tồn tại"}

        # 2. Kiểm tra số dư
        # Lưu ý: Database trả về Decimal hoặc int, cần đảm bảo so sánh đúng kiểu
        current_balance = acc.get("BALANCE") or 0
        if current_balance < amount:
            conn.rollback()
            return {"status": "error", "message": "Số dư không đủ"}

        # 3. Tạo Transaction ID
        tx_id = generate_sequential_id("T", "TRANSACTIONS", "TRANSACTION_ID", conn=conn)
        
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

        # 4. Tạo OTP trong DB (Dùng user_id từ account)
        user_id = acc.get("USER_ID")
        otp = create_otp_conn(conn, user_id, purpose="withdraw")
        
        # 5. Lấy EMAIL trực tiếp từ bảng USER bằng câu lệnh SQL
        # (Không gọi hàm từ user_model để tránh xung đột connection)
        user_email = None
        with conn.cursor() as cur:
            cur.execute("SELECT EMAIL FROM USER WHERE USER_ID = %s", (user_id,))
            user_row = cur.fetchone()
            if user_row:
                # Xử lý trường hợp row trả về dict hoặc tuple
                user_email = user_row["EMAIL"] if isinstance(user_row, dict) else user_row[0]

        # 6. Gửi Email
        if user_email:
            html_content = otp_email_template(otp["CODE"], purpose="Giao dịch Rút tiền")
            is_sent, error_msg = send_email(user_email, "Xác thực Rút tiền - ZY Banking", html_content)
            
            if not is_sent:
                conn.rollback()
                print(f"[MAIL ERROR] {error_msg}")
                return {"status": "error", "message": "Lỗi gửi email OTP. Vui lòng thử lại sau."}
        else:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản này chưa đăng ký Email."}

        conn.commit()
        return {
            "status": "success", 
            "transaction_id": tx_id, 
            "message": "Mã OTP đã được gửi tới email của bạn."
        }

    except Exception as e:
        conn.rollback()
        print(f"[SYSTEM ERROR] {e}")
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}
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
        return {"status": "error", "message": "Số tiền không hợp lệ"}

    conn = get_conn()
    try:
        conn.begin()
        
        # 1. Kiểm tra tài khoản nguồn
        src = get_account_by_id(conn, from_account_id)
        if not src:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản nguồn không tồn tại"}

        # 2. Kiểm tra số dư
        current_balance = src.get("BALANCE") or 0
        if current_balance < amount:
            conn.rollback()
            return {"status": "error", "message": "Số dư không đủ"}

        # 3. Kiểm tra tài khoản đích
        dest_name = None
        
        if to_bank_code == "LOCAL":
            # --- LOGIC NỘI BỘ (GIỮ NGUYÊN) ---
            dest = get_account_by_number(conn, to_account_number)
            if not dest:
                conn.rollback()
                return {"status": "error", "message": "Tài khoản người nhận không tồn tại trong hệ thống"}
            
            # Lấy tên người nhận nội bộ
            with conn.cursor() as cur:
                cur.execute("SELECT FULL_NAME FROM USER WHERE USER_ID = %s", (dest["USER_ID"],))
                u = cur.fetchone()
                if u:
                    dest_name = u["FULL_NAME"] if isinstance(u, dict) else u[0]
        else:
            # --- LOGIC LIÊN NGÂN HÀNG (MỚI) ---
            # Vì là external, ta không check DB. 
            # Giả lập tên người nhận để hiển thị cho đẹp lịch sử giao dịch.
            # Trong thực tế, bước này sẽ gọi API của NAPAS để tra cứu tên.
            dest_name = f"KHACH HANG {to_bank_code}" 

        # 4. Tạo Transaction
        tx_id = generate_sequential_id("T", "TRANSACTIONS", "TRANSACTION_ID", conn=conn)
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
            "DEST_ACC_NAME": dest_name, # Lưu tên người nhận (Thật hoặc Giả lập)
            "DEST_BANK_CODE": to_bank_code,
            "TYPE": "transfer"
        }
        # Lưu ý: Bạn cần đảm bảo bảng TRANSACTIONS có cột DESCRIPTION hoặc NOTE nếu muốn lưu note
        # Nếu chưa có cột đó, ta tạm bỏ qua biến 'note'
        
        insert_transaction(conn, tx)

        # 5. Tạo OTP cho người gửi
        user_id = src.get("USER_ID")
        otp = create_otp_conn(conn, user_id, purpose="transfer")
        
        # 6. Lấy EMAIL
        user_email = None
        with conn.cursor() as cur:
            cur.execute("SELECT EMAIL FROM USER WHERE USER_ID = %s", (user_id,))
            user_row = cur.fetchone()
            if user_row:
                user_email = user_row["EMAIL"] if isinstance(user_row, dict) else user_row[0]

        # 7. Gửi Email
        if user_email:
            # Tùy chỉnh nội dung email một chút cho chuyên nghiệp
            bank_display = "Nội bộ ZyBanking" if to_bank_code == "LOCAL" else to_bank_code
            email_subject = f"OTP Chuyển khoản tới {bank_display}"
            
            html_content = otp_email_template(otp["CODE"], purpose=f"Chuyển khoản tới {to_account_number} ({bank_display})")
            is_sent, error_msg = send_email(user_email, email_subject, html_content)
            
            if not is_sent:
                conn.rollback()
                print(f"[MAIL ERROR] {error_msg}")
                return {"status": "error", "message": "Lỗi gửi email OTP: " + error_msg}
        else:
            conn.rollback()
            return {"status": "error", "message": "Tài khoản chưa đăng ký Email"}

        conn.commit()
        return {
            "status": "success", 
            "transaction_id": tx_id, 
            "message": f"OTP đã gửi. Đang chuyển tới {to_bank_code}"
        }

    except Exception as e:
        conn.rollback()
        print(f"[SYSTEM ERROR] {e}")
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}
    finally:
        conn.close()

def transfer_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        
        # 1. Lấy thông tin giao dịch
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
        to_bank_code = tx["DEST_BANK_CODE"] # Lấy mã ngân hàng

        # 2. Lock tài khoản nguồn
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (source_account_id,))
            src = cur.fetchone()
            if not src:
                conn.rollback()
                return {"status": "error", "message": "Source account not found"}

        # 3. Validate OTP
        otp_row = get_valid_otp_conn(conn, src["USER_ID"], otp_code, "transfer")
        if not otp_row:
            conn.rollback()
            return {"status": "error", "message": "Invalid or expired OTP"}

        # 4. Check số dư lần cuối
        if (src["BALANCE"] or 0) < amount:
            conn.rollback()
            return {"status": "error", "message": "Insufficient balance"}

        # 5. Xử lý Tài khoản đích (CHỈ KHI LÀ LOCAL)
        dest = None
        if to_bank_code == "LOCAL":
            dest = get_account_by_number(conn, dest_acc_num)
            if not dest:
                # Trường hợp hiếm: lúc tạo thì có, giờ lại không thấy (xóa user?)
                conn.rollback()
                return {"status": "error", "message": "Destination account not found"}
            
            # Lock tài khoản đích để tránh xung đột
            with conn.cursor() as cur:
                cur.execute("SELECT ACCOUNT_ID FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (dest["ACCOUNT_ID"],))
        
        # 6. Mark OTP used
        mark_otp_used_conn(conn, otp_row["OTP_ID"])

        # 7. TRỪ TIỀN NGUỒN (Luôn thực hiện dù là Local hay External)
        with conn.cursor() as cur:
            cur.execute("UPDATE ACCOUNT SET BALANCE = BALANCE - %s WHERE ACCOUNT_ID = %s", (amount, source_account_id))

        # 8. CỘNG TIỀN ĐÍCH (Chỉ thực hiện nếu là LOCAL)
        if to_bank_code == "LOCAL" and dest:
            with conn.cursor() as cur:
                cur.execute("UPDATE ACCOUNT SET BALANCE = BALANCE + %s WHERE ACCOUNT_ID = %s", (amount, dest["ACCOUNT_ID"]))
        
        # Nếu là External: Tiền chỉ bị trừ ở nguồn, coi như đã chuyển sang hệ thống khác.

        # 9. Update Transaction Status
        update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        conn.commit()
        return {"status": "success", "message": "Transfer completed successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Transfer Confirm Error: {e}")
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

def get_user_by_account_service(account_number):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Đảm bảo tên cột ACCOUNT_NUMBER và FULL_NAME viết đúng như trong DB của bạn
            query = """
                SELECT U.FULL_NAME 
                FROM USER U
                JOIN ACCOUNT A ON U.USER_ID = A.USER_ID
                WHERE A.ACCOUNT_NUMBER = %s
            """
            cur.execute(query, (account_number,))
            row = cur.fetchone()
            
            if row:
                # Nếu fetchone() trả về dict (do dùng dictionary=True trong cursor)
                name = row.get("FULL_NAME") or row.get("full_name")
                return {"full_name": name}
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def verify_pin_service(transaction_id, pin_code):
    conn = get_conn()
    try:
        conn.begin()

        # 1. Lấy giao dịch
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx:
            conn.rollback()
            return {"status": "error", "message": "Transaction not found"}

        if tx["STATUS"] != "PENDING":
            conn.rollback()
            return {"status": "error", "message": "Transaction not pending"}

        # 2. Lock account nguồn
        account_id = tx["ACCOUNT_ID"]
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE",
                (account_id,)
            )
            acc = cur.fetchone()

        if not acc:
            conn.rollback()
            return {"status": "error", "message": "Account not found"}

        # 3. Verify PIN
        db_pin = acc.get("PIN_CODE")

        if not db_pin:
            conn.rollback()
            return {"status": "error", "message": "Account has no PIN set"}

        # ---- CASE 1: PIN LƯU DẠNG PLAINTEXT (DEMO) ----
        if str(db_pin) != str(pin_code):
            conn.rollback()
            return {"status": "error", "message": "Invalid PIN"}

        # ---- CASE 2: PIN HASH (KHUYẾN NGHỊ) ----
        # from werkzeug.security import check_password_hash
        # if not check_password_hash(db_pin, pin_code):
        #     conn.rollback()
        #     return {"status": "error", "message": "Invalid PIN"}

        # 4. Tạo OTP
        user_id = acc["USER_ID"]
        otp = create_otp_conn(conn, user_id, purpose=tx["TYPE"])

        # 5. Lấy EMAIL
        user_email = None
        with conn.cursor() as cur:
            cur.execute("SELECT EMAIL FROM USER WHERE USER_ID = %s", (user_id,))
            row = cur.fetchone()
            if row:
                user_email = row["EMAIL"] if isinstance(row, dict) else row[0]

        if not user_email:
            conn.rollback()
            return {"status": "error", "message": "User has no email"}

        # 6. Gửi Email OTP
        html = otp_email_template(
            otp["CODE"],
            purpose=f"Xác nhận giao dịch {tx['TYPE']}"
        )
        sent, err = send_email(
            user_email,
            "Xác thực giao dịch - ZY Banking",
            html
        )

        if not sent:
            conn.rollback()
            return {"status": "error", "message": "Failed to send OTP email"}

        conn.commit()
        return {
            "status": "success",
            "message": "PIN hợp lệ. OTP đã được gửi về Email"
        }

    except Exception as e:
        conn.rollback()
        print(f"[VERIFY PIN ERROR] {e}")
        return {"status": "error", "message": f"Server error: {e}"}
    finally:
        conn.close()

# --- GIAI ĐOẠN 1: TẠO YÊU CẦU VÀ GỬI OTP ---
def mortgage_payment_create_service(account_id, mortgage_id, amount):
    if amount is None or amount <= 0:
        return {"status": "error", "message": "Số tiền không hợp lệ"}

    conn = get_conn()
    try:
        conn.begin()
        with conn.cursor() as cur:
            # 1. Kiểm tra tài khoản nguồn (Checking Account)
            cur.execute("SELECT * FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (account_id,))
            acc = cur.fetchone()
            if not acc:
                return {"status": "error", "message": "Tài khoản thanh toán không tồn tại"}

            # 2. Kiểm tra số dư
            if (acc.get("BALANCE") or 0) < amount:
                return {"status": "error", "message": "Số dư không đủ để thanh toán"}

            # 3. Kiểm tra khoản vay (Bảng MORTAGE_DETAIL)
            # Lưu ý: Sửa tên cột trong câu điều kiện thành ACCOUNT_ID
            cur.execute("SELECT REMAINING_BALANCE, MORTAGE_ACC_ID FROM MORTAGE_DETAIL WHERE ACCOUNT_ID = %s", (mortgage_id,))
            mort = cur.fetchone()
            if not mort:
                return {"status": "error", "message": "Thông tin khoản vay không tồn tại"}
            
            # 4. Tạo giao dịch ở trạng thái PENDING
            tx_id = generate_sequential_id("T", "TRANSACTIONS", "TRANSACTION_ID", conn=conn)
            tx = {
                "TRANSACTION_ID": tx_id,
                "ACCOUNT_ID": account_id,
                "DEST_ACC_NUM": mortgage_id, # Lưu ID khoản vay vào đây để dùng lúc confirm
                "AMOUNT": amount,
                "TYPE": "mortgage_payment",
                "STATUS": "PENDING",
                "CREATED_AT": now()
            }
            insert_transaction(conn, tx)

            # 5. Tạo và gửi OTP qua Email
            user_id = acc.get("USER_ID")
            otp = create_otp_conn(conn, user_id, purpose="mortgage_payment")
            
            # Lấy email người dùng
            cur.execute("SELECT EMAIL FROM USER WHERE USER_ID = %s", (user_id,))
            user_row = cur.fetchone()
            user_email = user_row["EMAIL"] if isinstance(user_row, dict) else user_row[0]

            if user_email:
                html_content = otp_email_template(otp["CODE"], purpose="Thanh toán khoản vay")
                send_email(user_email, "Mã OTP thanh toán khoản vay", html_content)
            else:
                conn.rollback()
                return {"status": "error", "message": "Người dùng chưa đăng ký email"}

            conn.commit()
            return {
                "status": "success", 
                "transaction_id": tx_id, 
                "message": "Mã OTP đã được gửi đến email của bạn"
            }
    except Exception as e:
        conn.rollback()
        print(f"[MORTGAGE CREATE ERROR] {e}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

# --- GIAI ĐOẠN 2: XÁC NHẬN OTP VÀ TRỪ TIỀN THẬT ---
def mortgage_payment_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        # 1. Lấy thông tin giao dịch PENDING
        tx = get_transaction_by_id_conn(conn, transaction_id)
        if not tx or tx["STATUS"] != "PENDING":
            return {"status": "error", "message": "Giao dịch không hợp lệ hoặc đã xử lý"}

        account_id = tx["ACCOUNT_ID"]
        mortgage_id = tx["DEST_ACC_NUM"] # Lấy lại ID khoản vay đã lưu lúc nãy
        amount = tx["AMOUNT"]

        # 2. Lock tài khoản và kiểm tra OTP
        with conn.cursor() as cur:
            cur.execute("SELECT USER_ID, BALANCE FROM ACCOUNT WHERE ACCOUNT_ID = %s FOR UPDATE", (account_id,))
            acc = cur.fetchone()
            
            otp_row = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "mortgage_payment")
            if not otp_row:
                return {"status": "error", "message": "Mã OTP không đúng hoặc đã hết hạn"}

            # 3. THỰC HIỆN TRỪ TIỀN VÀ CẬP NHẬT NGÀY
        with conn.cursor() as cur:
            # Trừ tiền tài khoản chính
            cur.execute("UPDATE ACCOUNT SET BALANCE = BALANCE - %s WHERE ACCOUNT_ID = %s", (amount, account_id))
            
            # CẬP NHẬT QUAN TRỌNG:
            # 1. Trừ dư nợ gốc (REMAINING_BALANCE)
            # 2. Tăng ngày thanh toán tiếp theo lên 1 tháng (NEXT_PAYMENT_DATE)
            query_update_mortgage = """
                UPDATE MORTAGE_DETAIL 
                SET REMAINING_BALANCE = REMAINING_BALANCE - %s,
                    NEXT_PAYMENT_DATE = DATE_ADD(NEXT_PAYMENT_DATE, INTERVAL 1 MONTH)
                WHERE MORTAGE_ACC_ID = %s
            """
            cur.execute(query_update_mortgage, (amount, mortgage_id))

            # 4. Cập nhật trạng thái OTP và Giao dịch
            mark_otp_used_conn(conn, otp_row["OTP_ID"])
            update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        conn.commit()
        return {"status": "success", "message": "Thanh toán khoản vay thành công"}
    except Exception as e:
        conn.rollback()
        print(f"[MORTGAGE CONFIRM ERROR] {e}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

# -------------------------
# Savings Flow (Deposit to Savings)
# -------------------------

def savings_deposit_service(account_id, amount): # CHỈ NHẬN 2 THAM SỐ
    print(f"DEBUG: Nhận yêu cầu nạp tiền cho ID: {account_id}, Số tiền: {amount}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Bước 1: Tìm SAVING_ACC_ID từ bảng ACCOUNT
            cur.execute(
                "SELECT BALANCE, SAVING_ACC_ID FROM ACCOUNT WHERE ACCOUNT_ID=%s FOR UPDATE",
                (account_id,)
            )
            acc = cur.fetchone()
            
            if not acc:
                return {"status": "error", "message": "Không tìm thấy tài khoản"}
            
            # Lấy mã sổ tiết kiệm liên kết
            s_acc_id = acc.get("SAVING_ACC_ID")
            if not s_acc_id:
                return {"status": "error", "message": "Tài khoản không liên kết với sổ tiết kiệm nào"}

            # Bước 2: Kiểm tra sổ tiết kiệm trong bảng chi tiết
            cur.execute(
                "SELECT PRINCIPAL_AMOUNT FROM SAVING_DETAIL WHERE SAVING_ACC_ID=%s FOR UPDATE",
                (s_acc_id,)
            )
            saving_detail = cur.fetchone()
            if not saving_detail:
                return {"status": "error", "message": "Không tìm thấy chi tiết sổ tiết kiệm"}

            cur.execute(
                "UPDATE ACCOUNT SET BALANCE = BALANCE - %s WHERE ACCOUNT_ID=%s",
                (amount, account_id)
            )

            # 3.2. Cộng tiền vào bảng SAVING_DETAIL (Tiền gửi gốc)
            cur.execute(
                "UPDATE SAVING_DETAIL SET PRINCIPAL_AMOUNT = PRINCIPAL_AMOUNT + %s WHERE SAVING_ACC_ID=%s",
                (amount, s_acc_id)
            )
            tx_id = generate_sequential_id(
                "T", "TRANSACTIONS", "TRANSACTION_ID", conn=conn
            )

            insert_transaction(conn, {
                "TRANSACTION_ID": tx_id,
                "ACCOUNT_ID": account_id,
                "AMOUNT": amount,
                "TYPE": "savings_deposit",
                "STATUS": "COMPLETED",
                "CREATED_AT": now()
            })

        conn.commit()
        return {"status": "success", "message": "Gửi tiền tiết kiệm thành công"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def savings_withdraw_create_service(account_id, amount, pin):
    conn = get_conn()
    try:
        conn.begin()
        # 1. Kiểm tra mã PIN của tài khoản
        acc = get_account_by_id(conn, account_id)
        if str(acc.get("PIN_CODE")) != str(pin):
            return {"status": "error", "message": "Mã PIN không chính xác"}

        # 2. Kiểm tra số dư sổ tiết kiệm (Chỉ xem, không trừ)
        s_acc_id = acc.get("SAVING_ACC_ID")
        with conn.cursor() as cur:
            cur.execute("SELECT PRINCIPAL_AMOUNT FROM SAVING_DETAIL WHERE SAVING_ACC_ID=%s", (s_acc_id,))
            detail = cur.fetchone()
            if not detail or detail["PRINCIPAL_AMOUNT"] < amount:
                return {"status": "error", "message": "Số dư sổ tiết kiệm không đủ"}

        # 3. Tạo Transaction trạng thái PENDING
        tx_id = generate_sequential_id("T", "TRANSACTIONS", "TRANSACTION_ID", conn=conn)
        insert_transaction(conn, {
            "TRANSACTION_ID": tx_id,
            "ACCOUNT_ID": account_id,
            "AMOUNT": amount,
            "TYPE": "savings_withdraw",
            "STATUS": "PENDING", # Quan trọng: Để PENDING
            "CREATED_AT": now()
        })

        # 4. Tạo và gửi OTP qua Email
        acc = get_account_by_id(conn, account_id)
        user_id = acc.get("USER_ID")
        otp = create_otp_conn(conn, user_id, purpose="savings_withdraw")
        # Gọi hàm send_email của bạn ở đây...
        with conn.cursor() as cur:
            cur.execute("SELECT EMAIL FROM USER WHERE USER_ID = %s", (user_id,))
            user_row = cur.fetchone()
            user_email = user_row["EMAIL"] if isinstance(user_row, dict) else user_row[0]

        if user_email:
            html_content = otp_email_template(otp["CODE"], purpose="Rút tiền tiết kiệm")
            is_sent, error_msg = send_email(user_email, "Xác thực Rút tiền - ZY Banking", html_content)
            if not is_sent:
                conn.rollback()
                return {"status": "error", "message": "Không thể gửi email OTP"}
        
        conn.commit()
        return {"status": "success", "transaction_id": tx_id, "message": "OTP đã gửi"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

def savings_withdraw_confirm_service(transaction_id, otp_code):
    conn = get_conn()
    try:
        conn.begin()
        # 1. Kiểm tra OTP
        tx = get_transaction_by_id_conn(conn, transaction_id)
        acc = get_account_by_id(conn, tx["ACCOUNT_ID"])
        otp_row = get_valid_otp_conn(conn, acc["USER_ID"], otp_code, "savings_withdraw")
        
        if not otp_row:
            return {"status": "error", "message": "OTP sai hoặc hết hạn"}

        # 2. THỰC HIỆN TRỪ TIỀN THỰC SỰ
        s_acc_id = acc["SAVING_ACC_ID"]
        with conn.cursor() as cur:
            # Trừ tiền sổ tiết kiệm
            cur.execute("UPDATE SAVING_DETAIL SET PRINCIPAL_AMOUNT = PRINCIPAL_AMOUNT - %s WHERE SAVING_ACC_ID=%s", (tx["AMOUNT"], s_acc_id))
            # Cộng tiền tài khoản chính
            cur.execute("UPDATE ACCOUNT SET BALANCE = BALANCE + %s WHERE ACCOUNT_ID=%s", (tx["AMOUNT"], tx["ACCOUNT_ID"]))
            # Đổi trạng thái giao dịch
            update_transaction_status_conn(conn, transaction_id, "COMPLETED", complete_at=now())

        mark_otp_used_conn(conn, otp_row["OTP_ID"])
        conn.commit()
        return {"status": "success", "message": "Rút tiền tiết kiệm thành công"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()