from db import get_conn
class AccountModel:
    TABLE_NAME = "ACCOUNT"
    
    @staticmethod
    def _generate_account_id(cur):
        cur.execute(f"SELECT MAX(SUBSTRING(ACCOUNT_ID, 4)) AS max_id FROM {AccountModel.TABLE_NAME}")
        row = cur.fetchone()
        max_id = row["max_id"] if row and row["max_id"] is not None else 0
        next_id = int(max_id) + 1
        return f"ACC{next_id:02d}"


    @staticmethod
    def create(user_id, account_type, balance=0.0, interest_rate=0.0,
               status="active", account_number=None):

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                account_id = AccountModel._generate_account_id(cur)

                cur.execute(f"""
                    INSERT INTO {AccountModel.TABLE_NAME} 
                    (ACCOUNT_ID, USER_ID, ACCOUNT_TYPE, BALANCE, INTEREST_RATE, CREATED_AT, STATUS, ACCOUNT_NUMBER)
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s)
                """, (
                    account_id, user_id, account_type,
                    balance, interest_rate, status, account_number
                ))

                conn.commit()
                return account_id
        finally:
            conn.close()

    @staticmethod
    def list_all():
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM {AccountModel.TABLE_NAME}")
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_by_id(account_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {AccountModel.TABLE_NAME} WHERE ACCOUNT_ID=%s",
                    (account_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

    @staticmethod
    def update(account_id, **kwargs):
        if not kwargs:
            return

        keys = ", ".join([f"{k}=%s" for k in kwargs])
        values = list(kwargs.values())
        values.append(account_id)

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE {AccountModel.TABLE_NAME} SET {keys} WHERE ACCOUNT_ID=%s",
                    values
                )
                conn.commit()
        finally:
            conn.close()

class SavingDetailModel:
    TABLE_NAME = "SAVING_DETAIL"

    @staticmethod
    def create(account_id, principal_amount, interest_rate, term_months, start_date, maturity_date):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT MAX(SUBSTRING(SAVING_ACC_ID, 4)) AS max_id FROM {SavingDetailModel.TABLE_NAME}")
                row = cur.fetchone()
                max_id = int(row["max_id"]) if row and row["max_id"] else 0
                next_id = max_id + 1
                saving_acc_id = f"S{next_id:03d}"


                cur.execute(f"""
                    INSERT INTO {SavingDetailModel.TABLE_NAME} 
                    (SAVING_ACC_ID, ACCOUNT_ID, PRINCIPAL_AMOUNT, INTEREST_RATE,
                     TERM_MONTHS, START_DATE, MATURITY_DATE)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    saving_acc_id, account_id, principal_amount,
                    interest_rate, term_months, start_date, maturity_date
                ))

                conn.commit()
                return {"status": "success", "SAVING_ACC_ID": saving_acc_id}
        finally:
            conn.close()

    @staticmethod
    def get_by_account(account_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {SavingDetailModel.TABLE_NAME} WHERE ACCOUNT_ID=%s",
                    (account_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()

class MortageDetailModel:
    TABLE_NAME = "MORTAGE_DETAIL"

    @staticmethod
    def create(account_id, total_loan_amount, remaining_balance,
               paymen_frequency, payment_amount,
               next_payment_date, loan_end_date):

        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT MAX(SUBSTRING(MORTAGE_ACC_ID, 4)) AS max_id FROM {MortageDetailModel.TABLE_NAME}")
                row = cur.fetchone()
                max_id = int(row["max_id"]) if row and row["max_id"] else 0
                next_id = max_id + 1
                mortage_acc_id = f"M{next_id:03d}"

                cur.execute(f"""
                    INSERT INTO {MortageDetailModel.TABLE_NAME} 
                    (MORTAGE_ACC_ID, ACCOUNT_ID, TOTAL_LOAN_AMOUNT,
                     REMAINING_BALANCE, PAYMEN_FREQUENCY, PAYMENT_AMOUNT,
                     NEXT_PAYMENT_DATE, LOAN_END_DATE)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    mortage_acc_id, account_id, total_loan_amount, remaining_balance,
                    paymen_frequency, payment_amount,
                    next_payment_date, loan_end_date
                ))

                conn.commit()
                return {"status": "success", "MORTAGE_ACC_ID": mortage_acc_id}
        finally:
            conn.close()

    @staticmethod
    def get_by_account(account_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT * FROM {MortageDetailModel.TABLE_NAME} WHERE ACCOUNT_ID=%s",
                    (account_id,)
                )
                return cur.fetchone()
        finally:
            conn.close()
