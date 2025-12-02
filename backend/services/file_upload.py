import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"

def save_file(file):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath
