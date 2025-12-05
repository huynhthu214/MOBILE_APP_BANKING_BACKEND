from models.otp_model import OTPModel
import datetime, random

def generate_otp_code(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp(user_id, purpose="transaction"):
    otp_code = generate_otp_code()
    expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)

    # OTP_ID được sinh tự động trong model
    otp_id = OTPModel.create(user_id, otp_code, purpose, expires_at)

    return {
        "status": "success",
        "otp_id": otp_id,
        "code": otp_code,   # chỉ để test dev, production phải bỏ
        "message": "OTP sent"
    }


def verify_otp(user_id, code, purpose="transaction"):
    otp = OTPModel.get_latest(user_id, purpose)

    if not otp:
        return {"status": "error", "message": "OTP not found or expired"}

    if otp["CODE"] != code:
        return {"status": "error", "message": "Incorrect OTP"}

    if otp["IS_USED"]:
        return {"status": "error", "message": "OTP already used"}

    OTPModel.mark_used(otp["OTP_ID"])

    return {"status": "success", "message": "OTP verified"}


def list_otps():
    return {
        "status": "success",
        "data": OTPModel.list_all()
    }


def create_otp(user_id, purpose="transaction"):
    res = send_otp(user_id, purpose)
    return res["otp_id"], res["code"]


def verify_otp_util(user_id, code, purpose="transaction"):
    res = verify_otp(user_id, code, purpose)
    if res["status"] == "success":
        return True, res["message"]
    return False, res["message"]