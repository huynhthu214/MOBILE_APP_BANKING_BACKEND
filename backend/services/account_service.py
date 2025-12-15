from models.account_model import AccountModel, SavingDetailModel, MortageDetailModel
from models.transaction_model import get_transactions, create_transaction
from datetime import datetime, timedelta
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

    # CHECKING
    if acc_type == "checking":
        txs = get_transactions(account_id)
        last_10 = txs[:10] if len(txs) >= 10 else txs

        return {
            "status": "success",
            "type": "checking",
            "balance": acc["BALANCE"],
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
            "interest_rate": saving["INTEREST_RATE"],
            "monthly_interest": monthly_interest
        }

    # MORTGAGE
    if acc_type == "mortgage":
        mort = MortageDetailModel.get_by_account(account_id)
        if not mort:
            return {"status": "error", "message": "Mortgage detail not found"}

        return {
            "status": "success",
            "type": "mortgage",
            "remaining_balance": mort["REMAINING_BALANCE"],
            "next_payment_date": mort["NEXT_PAYMENT_DATE"]
        }

    return {"status": "error", "message": "Unsupported account type"}


# ===== SAVING DETAIL =====
def create_saving_detail(account_id, principal_amount, interest_rate, term_months, start_date=None, maturity_date=None):
    if start_date is None:
        start_date = datetime.now()
    if maturity_date is None:
        maturity_date = start_date + timedelta(days=30*term_months)  # tạm tính mỗi tháng 30 ngày
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
    # Optional: update luôn trong ACCOUNT
    AccountModel.update(account_id, INTEREST_RATE=new_rate)
    return {"status":"success", "SAVING_ACC_ID": saving["SAVING_ACC_ID"], "new_rate": new_rate}

def close_saving(account_id):
    saving = SavingDetailModel.get_by_account(account_id)
    if not saving:
        return {"status":"error","message":"Saving detail not found"}
    
    principal = saving["PRINCIPAL_AMOUNT"]
    rate = saving["INTEREST_RATE"]
    term = saving["TERM_MONTHS"]

    # tính lãi đơn giản
    interest = principal * (rate/100) * (term/12)
    total_amount = principal + interest

    # cập nhật balance account
    acc = AccountModel.get_by_id(account_id)
    new_balance = acc["BALANCE"] + total_amount
    AccountModel.update(account_id, BALANCE=new_balance)

    # đóng saving
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
    mortgage = MortageDetailModel.get_by_account(account_id)
    if not mortgage:
        return {"status":"error","message":"Mortgage detail not found"}

    acc = AccountModel.get_by_id(account_id)
    if acc["BALANCE"] < amount:
        return {"status":"error","message":"Insufficient balance"}

    # cập nhật dư nợ
    new_remaining = mortgage["REMAINING_BALANCE"] - amount
    MortageDetailModel.update_remaining(
        mortgage["MORTAGE_ACC_ID"], new_remaining
    )

    # tạo transaction chuẩn
    tx_id = create_withdraw(
        acc["USER_ID"],
        account_id,
        amount
    )

    return {
        "status": "success",
        "remaining_balance": new_remaining,
        "transaction_id": tx_id
    }

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
