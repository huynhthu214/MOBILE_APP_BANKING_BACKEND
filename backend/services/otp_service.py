from models.otp_model import OTPModel
import datetime, random

def generate_otp_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp(user_id, purpose="transaction"):
    otp_code = generate_otp_code()
    otp_id = f"O{int(datetime.datetime.now().timestamp())}"
    expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
    OTPModel.create(otp_id, user_id, otp_code, purpose, expires_at)
    return {"status": "success", "otp_id": otp_id, "code": otp_code, "message": "OTP sent"}

def verify_otp(user_id, code, purpose="transaction"):
    otp = OTPModel.get_latest(user_id, purpose)
    if not otp:
        return {"status": "error", "message": "OTP not found or expired"}
    if otp["CODE"] != code:
        return {"status": "error", "message": "Incorrect OTP"}
    OTPModel.mark_used(otp["OTP_ID"])
    return {"status": "success", "message": "OTP verified"}

def list_otps():
    return {"status": "success", "data": OTPModel.list_all()}
