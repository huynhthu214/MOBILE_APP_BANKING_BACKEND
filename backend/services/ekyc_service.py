from models.ekyc_model import (
    generate_ekyc_id,
    get_ekyc_by_user,
    insert_ekyc,
    update_ekyc_review,
    get_pending_ekyc,
    update_ekyc_images, 
    activate_user_after_ekyc,
    get_ekyc_by_id
)
import base64
from services.biometric_service import register_face
import datetime

def create_ekyc(user_id, data):
    existing_ekyc = get_ekyc_by_user(user_id)
    if existing_ekyc:
        status = existing_ekyc.get('STATUS')
        if status == 'rejected':
            # Redirect to update logic if rejected
            return update_ekyc(user_id, data)
        elif status == 'pending':
             return {"status":"error","message":"EKYC is pending approval","status_code":400}
        elif status == 'approved':
             return {"status":"error","message":"EKYC already approved","status_code":400}
        else:
             # Fallback for unknown status
             return {"status":"error","message":"EKYC record exists","status_code":400}

    # Dữ liệu nhận được là Base64 string
    front_b64 = data.get("ID_IMG_FRONT_URL")
    back_b64 = data.get("ID_IMG_BACK_URL")
    selfie_b64 = data.get("SELFIE_URL")

    if not all([front_b64, back_b64, selfie_b64]):
        return {"status":"error","message":"Missing images","status_code":400}

    # 1. Tích hợp Biometric: Đăng ký khuôn mặt ngay lập tức từ ảnh Selfie
    try:
        # Decode base64 thành bytes để thư viện face_recognition đọc được
        selfie_bytes = base64.b64decode(selfie_b64)
        
        # Gọi hàm register_face mà bạn đã có trong biometric_service.py
        # Hàm này sẽ tính toán embedding vector và lưu vào bảng USER_BIOMETRIC
        bio_result = register_face(user_id, selfie_bytes)
        
        print(f"Biometric registered: {bio_result}")
        
    except Exception as e:
        print(f"Biometric registration failed: {e}")
        # Tùy chọn: Có thể return lỗi nếu yêu cầu bắt buộc phải nhận diện được mặt
        return {"status":"error", "message": f"Face recognition failed: {str(e)}", "status_code": 400}

    # 2. Tạo eKYC Record
    ekyc_id = generate_ekyc_id()
    
    insert_ekyc((
        ekyc_id,
        user_id,
        front_b64, # Lưu base64 vào DB (hoặc lưu đường dẫn file nếu bạn viết code lưu file)
        back_b64,
        selfie_b64,
        "pending",
        None,
        None,
        datetime.datetime.now()
    ))

    return {
        "status":"success",
        "message":"EKYC submitted & Face Registered",
        "EKYC_ID": ekyc_id,
        "status_code":201
    }

def get_ekyc(user_id):
    ekyc = get_ekyc_by_user(user_id)
    if not ekyc:
        return {"status":"error","message":"EKYC not found","status_code":404}
    return {"status":"success","data":ekyc}


def review_ekyc(user_id, data):
    status = data.get("STATUS")
    reviewed_by = data.get("REVIEWED_BY")

    if status not in ["approved", "rejected"]:
        return {"status":"error","message":"Invalid STATUS","status_code":400}

    if not reviewed_by:
        return {"status":"error","message":"REVIEWED_BY required","status_code":400}

    if not get_ekyc_by_user(user_id):
        return {"status":"error","message":"EKYC not found","status_code":404}

    update_ekyc_review(user_id, status, reviewed_by)

    return {"status":"success","message":"EKYC reviewed"}

def get_pending_list():
    data = get_pending_ekyc()
    return {
        "status": "success",
        "data": data,
        "status_code": 200
    }
    
def update_ekyc(user_id, data):
    front_url = data.get("ID_IMG_FRONT_URL")
    back_url = data.get("ID_IMG_BACK_URL")
    selfie_url = data.get("SELFIE_URL")

    if not all([front_url, back_url, selfie_url]):
        return {"status":"error","message":"Missing image URLs","status_code":400}

    if not get_ekyc_by_user(user_id):
        return {"status":"error","message":"EKYC not found","status_code":404}

    affected = update_ekyc_images(user_id, front_url, back_url, selfie_url)
    if affected == 0:
        return {"status":"error","message":"EKYC not rejected or cannot update","status_code":400}

    return {"status":"success","message":"EKYC resubmitted","status_code":200}

def review_ekyc(user_id, data):
    status = data.get("STATUS")
    reviewed_by = data.get("REVIEWED_BY")

    if status not in ["approved", "rejected"]:
        return {"status":"error","message":"Invalid STATUS","status_code":400}

    if not reviewed_by:
        return {"status":"error","message":"REVIEWED_BY required","status_code":400}

    ekyc = get_ekyc_by_user(user_id)
    if not ekyc:
        return {"status":"error","message":"EKYC not found","status_code":404}

    update_ekyc_review(user_id, status, reviewed_by)

    if status == "approved":
        activate_user_after_ekyc(user_id, ekyc["EKYC_ID"])

    return {"status":"success","message":"EKYC reviewed"}

def get_ekyc_detail_by_id(ekyc_id):
    ekyc = get_ekyc_by_id(ekyc_id)

    if not ekyc:
        return {
            "status": "error",
            "message": "EKYC not found",
            "status_code": 404
        }

    return {
        "status": "success",
        "data": {
            "EKYC_ID": ekyc["EKYC_ID"],
            "USER_ID": ekyc["USER_ID"],
            "FULL_NAME": ekyc["FULL_NAME"],
            "EMAIL": ekyc["EMAIL"],
            "PHONE": ekyc["PHONE"],
            "IMG_FRONT_URL": ekyc["IMG_FRONT_URL"],
            "IMG_BACK_URL": ekyc["IMG_BACK_URL"],
            "SELFIE_URL": ekyc["SELFIE_URL"],
            "STATUS": ekyc["STATUS"],
            "REVIEWED_AT": ekyc["REVIEWED_AT"],
            "REVIEWED_BY": ekyc["REVIEWED_BY"],
            "CREATED_AT": ekyc["CREATED_AT"]
        },
        "status_code": 200
    }