from flask import Blueprint, request, jsonify
# from services.biometric_service import verify_face
from services.security_utils import decode_access_token

bp = Blueprint('biometric', __name__, url_prefix='/biometric/face')

@bp.route('/register', methods=['POST'])
def register_face_route():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"status":"error","message":"Missing access token"}), 401

    token = auth_header.split(' ')[1]
    payload, err = decode_access_token(token)
    if err:
        return jsonify({"status":"error","message":err}), 401

    user_id = payload.get('sub')

    file = request.files.get('face_image')
    if not file:
        return jsonify({"status":"error","message":"No face image uploaded"}), 400

    face_bytes = file.read()
    result = register_face(user_id, face_bytes)
    return jsonify(result)

@bp.route('/verify', methods=['POST'])
def verify_face_route():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"status":"error","message":"Missing access token"}), 401

    token = auth_header.split(' ')[1]
    payload, err = decode_access_token(token)
    if err:
        return jsonify({"status":"error","message":err}), 401

    user_id = payload.get('sub')

    file = request.files.get('face_image')
    if not file:
        return jsonify({"status":"error","message":"No face image uploaded"}), 400

    face_bytes = file.read()
    result = verify_face(user_id, face_bytes)
    return jsonify(result)
