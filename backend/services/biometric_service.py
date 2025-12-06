from models.user_biometric_model import UserBiometricModel
import face_recognition
import numpy as np
import numpy as np
from io import BytesIO
from PIL import Image

def get_face_embedding(image_bytes):
    # Mở ảnh
    image = Image.open(BytesIO(image_bytes))
    
    # Ép RGB và 8-bit
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Resize để giảm load
    max_size = 800
    w, h = image.size
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS
        image = image.resize((int(w*scale), int(h*scale)), resample)

    # Chuyển sang numpy array uint8, C-contiguous
    image_np = np.ascontiguousarray(np.array(image, dtype=np.uint8))
    
    # Debug: kiểm tra shape và dtype
    print("Image shape:", image_np.shape, "dtype:", image_np.dtype)

    # Lấy embedding
    embeddings = face_recognition.face_encodings(image_np)
    if len(embeddings) == 0:
        raise ValueError("No face detected")
    return embeddings[0]

def register_face(user_id, face_image_bytes):
    embedding = get_face_embedding(face_image_bytes)
    biometric_id = UserBiometricModel.register_face(user_id, embedding)
    return {"status":"success", "biometric_id": biometric_id}

def verify_face(user_id, face_image_bytes, threshold=0.6):
    embedding = get_face_embedding(face_image_bytes)
    stored = UserBiometricModel.get_face(user_id)
    if not stored:
        return {"status":"error", "message":"No face registered"}

    stored_embedding = np.array(stored['FACE_TEMPLATE_HASH'])
    # cosine similarity
    similarity = np.dot(embedding, stored_embedding) / (np.linalg.norm(embedding)*np.linalg.norm(stored_embedding))
    if similarity >= threshold:
        return {"status":"success", "message":"Face verified"}
    else:
        return {"status":"error", "message":"Face mismatch"}
