from models.ekyc_model import (
    generate_ekyc_id,
    get_ekyc_by_user,
    insert_ekyc,
    update_ekyc_review,
    bind_ekyc_to_user
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

    bind_ekyc_to_user(user_id, ekyc_id)

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
