import os, uuid, base64

UPLOAD_FOLDER = "uploads"

def save_file_base64(base64_str):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    try:
        file_data = base64.b64decode(base64_str)
    except Exception:
        return None

    filename = f"{uuid.uuid4().hex}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)

    with open(path, "wb") as f:
        f.write(file_data)

    return f"/uploads/{filename}"


def delete_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(path):
        return False

    os.remove(path)
    return True
