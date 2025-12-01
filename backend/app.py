from flask import Flask
from routes.auth import bp as auth_bp
from routes.users import bp as users_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
if __name__ == "__main__":
    app.run(debug=True)
