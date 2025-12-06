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
import datetime

def create_ekyc(user_id, data):
    if get_ekyc_by_user(user_id):
        return {"status":"error","message":"EKYC already exists","status_code":400}

    front_url = data.get("ID_IMG_FRONT_URL")
    back_url = data.get("ID_IMG_BACK_URL")
    selfie_url = data.get("SELFIE_URL")

    if not all([front_url, back_url, selfie_url]):
        return {"status":"error","message":"Missing image URLs","status_code":400}

    ekyc_id = generate_ekyc_id()

    insert_ekyc((
        ekyc_id,
        user_id,
        front_url,
        back_url,
        selfie_url,
        "pending",
        None,
        None,
        datetime.datetime.now()
    ))

    return {
        "status":"success",
        "message":"EKYC submitted",
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