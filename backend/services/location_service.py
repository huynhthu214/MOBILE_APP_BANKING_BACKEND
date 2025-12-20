from datetime import datetime
import math
from db import get_conn
from models.location_model import (
    get_all_locations,
    get_location_by_id,
    insert_location,
    update_location,
    delete_location
)

# ============================
# Sinh BRANCH_ID dạng LOC01
# ============================
def generate_branch_id():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT BRANCH_ID FROM LOCATION ORDER BY BRANCH_ID DESC LIMIT 1")
            last = cur.fetchone()

            if not last:
                return "LOC01"

            last_num = int(last["BRANCH_ID"].replace("LOC", ""))
            return f"LOC{last_num + 1:02d}"
    finally:
        conn.close()


# ============================
# Công thức Haversine
# ============================
def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)

    a = math.sin(d_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ============================
# Tìm chi nhánh gần nhất
# ============================
def find_nearby_branches(user_lat, user_lng, radius_m):
    branches = get_all_locations()
    result = []

    user_lat = float(user_lat)
    user_lng = float(user_lng)

    for b in branches:
        if b["LAT"] is None or b["LNG"] is None:
            continue

        b_lat = float(b["LAT"])
        b_lng = float(b["LNG"])

        if b_lat == 0 or b_lng == 0:
            continue

        distance = haversine_distance(
            user_lat, user_lng,
            b_lat, b_lng
        )

        if distance <= radius_m:
            b["DISTANCE_M"] = round(distance, 2)
            result.append(b)

    result.sort(key=lambda x: x["DISTANCE_M"])
    return result

# ============================
# Tính route đơn giản
# ============================
def calculate_simple_route(branch_id, from_lat, from_lng):
    branch = get_location_by_id(branch_id)

    if not branch:
        return None

    distance = haversine_distance(
        from_lat, from_lng,
        float(branch["LAT"]), float(branch["LNG"])
    )

    return {
        "FROM": {
            "LAT": from_lat,
            "LNG": from_lng
        },
        "TO": {
            "BRANCH_ID": branch["BRANCH_ID"],
            "NAME": branch["NAME"],
            "LAT": float(branch["LAT"]),
            "LNG": float(branch["LNG"])
        },
        "DISTANCE_M": round(distance, 2),
        "ESTIMATED_TIME_MIN": round(distance / 300, 1)
    }


# ============================
# CRUD
# ============================
def create_branch(data):
    branch_id = generate_branch_id()

    values = (
        branch_id,
        data.get("NAME"),
        data.get("ADDRESS"),
        data.get("LAT"),
        data.get("LNG"),
        data.get("OPEN_HOURS"),
        datetime.now()
    )

    try:
        insert_location(values)
        return {"message": "created", "BRANCH_ID": branch_id}
    except Exception as e:
        return {"message": "error", "error": str(e)}


def get_all_branches():
    return get_all_locations()


def get_branch_by_id_service(branch_id):
    return get_location_by_id(branch_id)


def update_branch(branch_id, data):
    values = (
        data.get("NAME"),
        data.get("ADDRESS"),
        data.get("LAT"),
        data.get("LNG"),
        data.get("OPEN_HOURS")
    )

    rowcount = update_location(branch_id, values)

    if rowcount == 0:
        return {"message": "not_found"}

    return {"message": "updated"}


def delete_branch(branch_id):
    rowcount = delete_location(branch_id)

    if rowcount == 0:
        return {"message": "not_found"}

    return {"message": "deleted"}
