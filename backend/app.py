from flask import Flask
from routes.auth import bp as auth_bp
from routes.users import bp as users_bp
from routes.payments import bp as payments_bp
from routes.transactions import bp as transactions_bp
# from routes.utility import bp as utility_bp
from routes.ekyc import bp as ekyc_bp
from routes.files import bp as files_bp
from routes.otp import bp as otp_bp
from routes.accounts import bp as account_bp
from routes.location import bp as location_bp
from routes.system import bp as system_bp
from routes.biometric import bp as biometric_bp
from routes.admin import bp_admin

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)    
app.register_blueprint(payments_bp)   
app.register_blueprint(transactions_bp)
# app.register_blueprint(utility_bp)
app.register_blueprint(ekyc_bp)
app.register_blueprint(files_bp)
app.register_blueprint(otp_bp)
app.register_blueprint(account_bp)
app.register_blueprint(location_bp)
app.register_blueprint(system_bp)
app.register_blueprint(biometric_bp)
app.register_blueprint(bp_admin)

if __name__ == "__main__":
    app.run(debug=True)
