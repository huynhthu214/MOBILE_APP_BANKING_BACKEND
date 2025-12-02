from models.account_model import AccountModel, SavingDetailModel, MortageDetailModel
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
