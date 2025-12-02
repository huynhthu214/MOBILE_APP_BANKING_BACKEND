from flask import Flask, request, jsonify
from user_service import create_user, get_user_detail, update_user_info, list_users

app = Flask(__name__)

@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.json
    return jsonify(create_user(data)), create_user(data)["status_code"]

@app.route("/api/users/<user_id>", methods=["GET"])
def api_get_user(user_id):
    result = get_user_detail(user_id)
    status_code = result.get("status_code", 200)  # default 200 nếu không có
    return jsonify(result), status_code

@app.route("/api/users/<user_id>", methods=["PUT"])
def api_update_user(user_id):
    data = request.json
    result = update_user_info(user_id, data)
    status_code = result.get("status_code", 200)
    return jsonify(result), status_code


@app.route("/api/users", methods=["GET"])
def api_list_users():
    keyword = request.args.get("keyword", "")
    return jsonify(list_users(keyword)), 200

if __name__ == "__main__":
    app.run(debug=True)
