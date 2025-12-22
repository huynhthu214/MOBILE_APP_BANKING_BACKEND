from flask import Flask

from routes.auth import bp as auth_bp
from routes.users import bp as users_bp, admin_bp
from routes.payments import bp as payments_bp
from routes.transactions import bp as transactions_bp
from routes.bills import bp as bills_bp
from routes.utility import bp as utility_bp
from routes.ekyc import bp as ekyc_bp
from routes.files import bp as files_bp
from routes.otp import bp as otp_bp
from routes.accounts import bp as account_bp
from routes.location import bp as location_bp
from routes.system import bp as system_bp
from routes.biometric import bp as biometric_bp
from routes.admin import bp_admin
from routes.noti import bp as bp_noti
from routes.admin_dashboard import admin_dashboard_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)    
app.register_blueprint(payments_bp)   
app.register_blueprint(transactions_bp)
app.register_blueprint(bills_bp)
app.register_blueprint(utility_bp)
app.register_blueprint(ekyc_bp)
app.register_blueprint(files_bp)
app.register_blueprint(otp_bp)
app.register_blueprint(account_bp)
app.register_blueprint(location_bp)
app.register_blueprint(system_bp)
app.register_blueprint(biometric_bp)
app.register_blueprint(bp_admin)
app.register_blueprint(bp_noti)
app.register_blueprint(admin_bp)
app.register_blueprint(admin_dashboard_bp, url_prefix='/api/v1')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

@app.route("/mock/vnpay")
def mock_vnpay():
    pid = request.args.get("pid")
    amount = request.args.get("amount")

    return f"""
    <h2>VNPay Sandbox</h2>
    <p>Số tiền: {amount} VND</p>
    <a href="/api/v1/payments/callback?pid={pid}&result=success">
        Thanh toán thành công
    </a><br><br>
    <a href="/api/v1/payments/callback?pid={pid}&result=fail">
        Hủy
    </a>
    """

@app.route("/mock/stripe")
def mock_stripe():
    pid = request.args.get("pid")
    amount = request.args.get("amount")

    return f"""
    <h2>Stripe Checkout</h2>
    <p>Amount: {amount} VND</p>
    <a href="/api/v1/payments/callback?pid={pid}&result=success">
        Pay
    </a><br><br>
    <a href="/api/v1/payments/callback?pid={pid}&result=fail">
        Cancel
    </a>
    """
