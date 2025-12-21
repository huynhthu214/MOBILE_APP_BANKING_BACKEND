from models.account_model import AccountModel, SavingDetailModel, MortageDetailModel
from models.transaction_model import TransactionModel
from services.transaction_service import generate_sequential_id
from datetime import datetime, timedelta
from db import get_conn
import json
import os
# ===== ACCOUNT =====
def create_account(user_id, account_type, balance=0.0, interest_rate=0.0, status="active", account_number=None):
    account_id = AccountModel.create(
        user_id=user_id,
        account_type=account_type,
        balance=balance,
        interest_rate=interest_rate,
        status=status,
        account_number=account_number
    )
    return {
        "status": "success",
        "message": "Account created",
        "ACCOUNT_ID": account_id
    }

def list_accounts():
    return {"status": "success", "data": AccountModel.list_all()}

def get_transactions(account_id, limit=None):
    # LƯU Ý: Đảm bảo bạn đã thêm hàm get_by_account vào TransactionModel như hướng dẫn trước
    # Nếu chưa, hãy đổi dòng dưới thành: txs = TransactionModel.list_all(account_id)
    txs = TransactionModel.get_by_account(account_id) 
    if limit:
        return txs[:limit]
    return txs

def get_account(account_id):
    account = AccountModel.get_by_id(account_id)
    if not account:
        return {"status": "error", "message": "Account not found"}
    return {"status": "success", "data": account}

def update_account(account_id, **kwargs):
    AccountModel.update(account_id, **kwargs)
    return {"status": "success", "message": "Account updated"}

def get_account_summary(account_id):
    acc = AccountModel.get_by_id(account_id)
    if not acc:
        return {"status": "error", "message": "Account not found"}

    acc_type = acc["ACCOUNT_TYPE"].lower()
    
    # Get Account Number if available
    acc_num = acc.get("ACCOUNT_NUMBER")

    # CHECKING
    if acc_type == "checking":
        txs = get_transactions(account_id)
        last_10 = txs[:10] if len(txs) >= 10 else txs

        return {
            "status": "success",
            "type": "checking",
            "balance": acc["BALANCE"],
            "account_number": acc_num,
            "last_transactions": last_10
        }

    # SAVING
    if acc_type == "saving":
        saving = SavingDetailModel.get_by_account(account_id)
        if not saving:
            return {"status": "error", "message": "Saving detail not found"}

        monthly_interest = saving["PRINCIPAL_AMOUNT"] * saving["INTEREST_RATE"] / 12

        return {
            "status": "success",
            "type": "saving",
            "balance": acc["BALANCE"],
            "account_number": acc_num,
            "interest_rate": saving["INTEREST_RATE"],
            "monthly_interest": monthly_interest,
            "principal": saving["PRINCIPAL_AMOUNT"],
            "maturity_date": saving["MATURITY_DATE"]
        }

# MORTGAGE
    if acc_type == "mortgage":
        mort = MortageDetailModel.get_by_account(account_id)
        if not mort:
            return {"status": "error", "message": "Mortgage detail not found"}

        return {
            "status": "success",
            "type": "mortgage",
            "account_number": acc.get("ACCOUNT_NUMBER"),
            "remaining_balance": mort["REMAINING_BALANCE"],
            "next_payment_date": mort["NEXT_PAYMENT_DATE"],
            "payment_amount": mort["PAYMENT_AMOUNT"],
            "loan_end_date": mort["LOAN_END_DATE"], 
            "payment_frequency": mort["PAYMEN_FREQUENCY"], 
            "total_loan_amount": mort["TOTAL_LOAN_AMOUNT"],
            "interest_rate": acc["INTEREST_RATE"]
        }


# ===== SAVING DETAIL =====
def create_saving_detail(account_id, principal_amount, interest_rate, term_months, start_date=None, maturity_date=None):
    if start_date is None:
        start_date = datetime.now()
    if maturity_date is None:
        maturity_date = start_date + timedelta(days=30*term_months)
    result = SavingDetailModel.create(
        account_id, principal_amount, interest_rate, term_months, start_date, maturity_date
    )
    return result

def get_saving_detail(account_id):
    data = SavingDetailModel.get_by_account(account_id)
    return {"status": "success", "data": data}

def update_saving_interest(account_id, new_rate):
    saving = SavingDetailModel.get_by_account(account_id)
    if not saving:
        return {"status":"error", "message":"Saving detail not found"}
    
    SavingDetailModel.update_interest(saving["SAVING_ACC_ID"], new_rate)
    AccountModel.update(account_id, INTEREST_RATE=new_rate)
    return {"status":"success", "SAVING_ACC_ID": saving["SAVING_ACC_ID"], "new_rate": new_rate}

def close_saving(account_id):
    saving = SavingDetailModel.get_by_account(account_id)
    if not saving:
        return {"status":"error","message":"Saving detail not found"}
    
    principal = saving["PRINCIPAL_AMOUNT"]
    rate = saving["INTEREST_RATE"]
    term = saving["TERM_MONTHS"]

    interest = principal * (rate/100) * (term/12)
    total_amount = principal + interest

    acc = AccountModel.get_by_id(account_id)
    new_balance = acc["BALANCE"] + total_amount
    AccountModel.update(account_id, BALANCE=new_balance)

    SavingDetailModel.close_saving(saving["SAVING_ACC_ID"])

    return {"status":"success", "total_paid": total_amount, "principal": principal, "interest": interest}

def get_saving_profit(account_id):
    acc = AccountModel.get_by_id(account_id)
    if not acc or acc["ACCOUNT_TYPE"].lower() != "saving":
        return {"status": "error", "message": "Saving account not found"}

    saving = SavingDetailModel.get_by_account(account_id)
    if not saving:
        return {"status": "error", "message": "Saving detail not found"}

    principal = saving["PRINCIPAL_AMOUNT"]
    rate = saving["INTEREST_RATE"]
    term = saving["TERM_MONTHS"]

    total_interest = principal * (rate / 100) * (term / 12)
    total_profit = principal + total_interest

    return {
        "status": "success",
        "principal": principal,
        "interest_rate": rate,
        "term_months": term,
        "total_interest": round(total_interest, 2),
        "total_profit": round(total_profit, 2),
        "maturity_date": saving["MATURITY_DATE"]
    }
    
# ===== MORTAGE DETAIL =====
def create_mortage_detail(account_id, total_loan_amount, remaining_balance, paymen_frequency,
                          payment_amount, next_payment_date, loan_end_date):
    result = MortageDetailModel.create(
        account_id, total_loan_amount, remaining_balance,
        paymen_frequency, payment_amount,
        next_payment_date, loan_end_date
    )
    return result

def get_mortage_detail(account_id):
    data = MortageDetailModel.get_by_account(account_id)
    return {"status": "success", "data": data}

def pay_mortgage(account_id, amount):
    # --- FIX QUAN TRỌNG: Import ở đây để tránh lỗi circular dependency ---
    from services.transaction_service import create_transaction
    # ---------------------------------------------------------------------

    mortgage = MortageDetailModel.get_by_account(account_id)
    if not mortgage:
        return {"status":"error","message":"Mortgage detail not found"}

    remaining = mortgage["REMAINING_BALANCE"]
    if amount > remaining:
        return {"status":"error","message":"Amount exceeds remaining balance"}

    new_remaining = remaining - amount
    MortageDetailModel.update_remaining(mortgage["MORTAGE_ACC_ID"], new_remaining)

    tx_id = generate_sequential_id("T", "TRANSACTION", "TRANSACTION_ID") # Lưu ý tên bảng là TRANSACTION hay TRANSACTIONS?
    acc = AccountModel.get_by_id(account_id)

    tx_data = {
        "transaction_id": tx_id,
        "payment_id": None,
        "account_id": account_id,
        "amount": amount,
        "currency": "VND",
        "account_type": acc["ACCOUNT_TYPE"],
        "status": "COMPLETED",
        "type": "MORTGAGE_PAYMENT"
    }

    create_transaction(tx_data) # Giờ đã gọi được hàm này

    return {"status":"success", "mortgage_acc_id": mortgage["MORTAGE_ACC_ID"], "remaining_balance": new_remaining, "transaction_id": tx_id}

def get_mortgage_schedule(account_id):
    acc = AccountModel.get_by_id(account_id)
    if not acc or acc["ACCOUNT_TYPE"].lower() != "mortgage":
        return {"status":"error","message":"Mortgage account not found"}

    mort = MortageDetailModel.get_by_account(account_id)
    if not mort:
        return {"status":"error","message":"Mortgage detail not found"}

    remaining = mort["REMAINING_BALANCE"]
    payment_amount = mort["PAYMENT_AMOUNT"]
    frequency = mort["PAYMEN_FREQUENCY"]
    next_date = mort["NEXT_PAYMENT_DATE"]

    schedule = []
    current_balance = remaining
    current_date = next_date
    i = 1

    while current_balance > 0:
        pay = min(payment_amount, current_balance)
        current_balance -= pay

        schedule.append({
            "period": i,
            "payment_date": current_date,
            "amount": pay,
            "remaining_balance": round(current_balance, 2)
        })

        if frequency == "monthly":
            current_date = current_date + timedelta(days=30)
        elif frequency == "biweekly":
            current_date = current_date + timedelta(days=14)
        else:
            break

        i += 1

    return {
        "status": "success",
        "account_id": account_id,
        "schedule": schedule
    }

def update_global_rates(new_rates):
    # 1. Lưu vào file JSON (để hiển thị lên UI Admin)
    current = get_rates_from_file()
    current.update(new_rates)
    save_rates_to_file(current)

    # 2. Cập nhật Mortgage (Vay thế chấp)
    if 'rate_mortgage' in new_rates:
        try:
            # Cập nhật bảng ACCOUNT cho loại mortgage
            update_mortgage_accounts_bulk(float(new_rates['rate_mortgage']))
        except ValueError: pass

    # 3. Cập nhật Savings (Tiết kiệm) theo từng kỳ hạn
    # Kiểm tra từng loại kỳ hạn gửi lên và update vào SQL
    if 'rate_1m' in new_rates:
        try:
            update_savings_bulk(1, float(new_rates['rate_1m'])) # 1 tháng
        except ValueError: pass

    if 'rate_6m' in new_rates:
        try:
            update_savings_bulk(6, float(new_rates['rate_6m'])) # 6 tháng
        except ValueError: pass

    if 'rate_12m' in new_rates:
        try:
            update_savings_bulk(12, float(new_rates['rate_12m'])) # 12 tháng
        except ValueError: pass

    return {"status": "success", "message": "Đã cập nhật lãi suất thành công"}

RATES_FILE = "rates.json"  # Tên file lưu cấu hình lãi suất

def get_rates_from_file():
    if not os.path.exists(RATES_FILE):
        # Tạo file mặc định nếu chưa tồn tại
        default_rates = {"rate_12m": 5.5, "rate_mortgage": 7.5}
        save_rates_to_file(default_rates)
        return default_rates
    
    try:
        with open(RATES_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {"rate_12m": 5.5, "rate_mortgage": 7.5}

def save_rates_to_file(rates):
    try:
        with open(RATES_FILE, 'w') as f:
            json.dump(rates, f, indent=4)
    except Exception as e:
        print(f"Error saving rates: {e}")

def update_mortgage_accounts_bulk(new_rate):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Chỉ update những tài khoản là mortgage
            sql = "UPDATE ACCOUNT SET INTEREST_RATE = %s WHERE ACCOUNT_TYPE = 'mortgage'"
            cur.execute(sql, (new_rate,))
            conn.commit()
            print(f"Updated mortgage rate to {new_rate}% for all mortgage accounts.")
    except Exception as e:
        print(f"Error bulk updating mortgage: {e}")
    finally:
        conn.close()
    
def update_savings_bulk(term_months, new_rate):
    """Cập nhật lãi suất cho các sổ tiết kiệm có kỳ hạn cụ thể"""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Chỉ update những dòng có TERM_MONTHS khớp với input
            sql = "UPDATE SAVING_DETAIL SET INTEREST_RATE = %s WHERE TERM_MONTHS = %s"
            cur.execute(sql, (new_rate, term_months))
            conn.commit()
            print(f"Updated savings with term {term_months} months to {new_rate}%")
    except Exception as e:
        print(f"Error updating savings term {term_months}: {e}")
    finally:
        conn.close()