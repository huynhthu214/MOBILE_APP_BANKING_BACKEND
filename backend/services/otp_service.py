from models.otp_model import OTPModel
import datetime, random
from services.mail_service import send_email
from services.mail_templates import otp_email_template
from models.user_model import get_user_by_id

def generate_otp_code(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

# =====================
# INTERNAL UTIL (CHECK DB)
# =====================
def verify_otp_util(user_id, otp_code, purpose="transaction", mark_used=True):
    otp = OTPModel.get_latest_valid_otp(user_id, purpose)
    print("DEBUG: OTP fetched from DB:", otp)

    if not otp:
        return False, "OTP not found"

    if otp["CODE"] != otp_code:
        return False, "Invalid OTP"

    # Convert EXPIRES_AT to datetime if it's string
    expires_at = otp["EXPIRES_AT"]
    if isinstance(expires_at, str):
        expires_at = datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
    if expires_at < datetime.datetime.now():
        return False, "OTP expired"

    if mark_used:
        OTPModel.mark_used(otp["OTP_ID"])
    return True, "OTP valid"

# =====================
# API FUNCTION
# =====================
def create_otp(user_id, purpose="transaction"):
    otp_code = generate_otp_code()

    # Thời gian expire để test: forgot_password 5 phút, transaction 10 phú
    expires_at = (
        datetime.datetime.now() + datetime.timedelta(minutes=5)
        if purpose == "forgot_password"
        else datetime.datetime.now() + datetime.timedelta(minutes=10)
    )

    otp_id = OTPModel.create(user_id, otp_code, purpose, expires_at)
    print(f"DEBUG: Created OTP {otp_code} for user {user_id}, expires at {expires_at}")

    user = get_user_by_id(user_id)
    if user and user.get("EMAIL"):
        html = otp_email_template(otp_code, purpose)
        send_email(
            user["EMAIL"],
            "Your OTP Code - ZY Banking",
            html
        )

    return otp_id, otp_code
