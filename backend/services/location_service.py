from db import get_conn
from datetime import datetime


# ============================
# Sinh BRANCH_ID dạng LOC01, LOC02...
# ============================
def generate_branch_id():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT BRANCH_ID FROM LOCATION ORDER BY BRANCH_ID DESC LIMIT 1")
    last = cursor.fetchone()

    if not last:
        new_id = "LOC01"
    else:
        last_num = int(last["BRANCH_ID"].replace("LOC", ""))
        new_id = f"LOC{last_num + 1:02d}"

    cursor.close()
    conn.close()
    return new_id


# ============================
# POST /api/v1/branches
# ============================
def create_branch(data):
    conn = get_conn()
    cursor = conn.cursor()

    branch_id = generate_branch_id()
    name = data.get("NAME")
    address = data.get("ADDRESS")
    lat = data.get("LAT")
    lng = data.get("LNG")
    open_hours = data.get("OPEN_HOURS")
    created_at = datetime.now()

    sql = """
        INSERT INTO LOCATION
        (BRANCH_ID, NAME, ADDRESS, LAT, LNG, OPEN_HOURS, CREATED_AT)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (branch_id, name, address, lat, lng, open_hours, created_at)

    try:
        cursor.execute(sql, values)
        conn.commit()
        return {"message": "created", "BRANCH_ID": branch_id}
    except Exception as e:
        return {"message": "error", "error": str(e)}
    finally:
        cursor.close()
        conn.close()


# ============================
# GET /api/v1/branches
# ============================
def get_all_branches():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM LOCATION ORDER BY BRANCH_ID ASC")
    data = cursor.fetchall()

    cursor.close()
    conn.close()
    return data


# ============================
# GET /api/v1/branches/{id}
# ============================
def get_branch_by_id(branch_id):
    conn = get_conn()
    cursor = conn.cursor()

    sql = "SELECT * FROM LOCATION WHERE BRANCH_ID = %s"
    cursor.execute(sql, (branch_id,))
    data = cursor.fetchone()

    cursor.close()
    conn.close()
    return data


# ============================
# PUT /api/v1/branches/{id}
# ============================
def update_branch(branch_id, data):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
        UPDATE LOCATION SET
        NAME = %s,
        ADDRESS = %s,
        LAT = %s,
        LNG = %s,
        OPEN_HOURS = %s
        WHERE BRANCH_ID = %s
    """

    values = (
        data.get("NAME"),
        data.get("ADDRESS"),
        data.get("LAT"),
        data.get("LNG"),
        data.get("OPEN_HOURS"),
        branch_id
    )

    try:
        cursor.execute(sql, values)
        conn.commit()

        if cursor.rowcount == 0:
            return {"message": "not_found"}

        return {"message": "updated"}
    except Exception as e:
        return {"message": "error", "error": str(e)}
    finally:
        cursor.close()
        conn.close()


# ============================
# DELETE /api/v1/branches/{id}
# ============================
def delete_branch(branch_id):
    conn = get_conn()
    cursor = conn.cursor()

    sql = "DELETE FROM LOCATION WHERE BRANCH_ID = %s"

    try:
        cursor.execute(sql, (branch_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return {"message": "not_found"}

        return {"message": "deleted"}
    except Exception as e:
        return {"message": "error", "error": str(e)}
    finally:
        cursor.close()
        conn.close()
