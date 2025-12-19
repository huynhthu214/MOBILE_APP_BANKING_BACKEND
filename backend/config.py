# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "HOST": os.getenv("DB_HOST", "localhost"),
    "USER": os.getenv("DB_USER", "root"),
    "PASSWORD": os.getenv("DB_PASS", ""),
    "NAME": os.getenv("DB_NAME", "zybank"),
    "PORT": int(os.getenv("DB_PORT", "3306"))
}

JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_EXPIRE_MIN = int(os.getenv("ACCESS_EXPIRE_MIN", "15"))  # minutes
REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_EXPIRE_DAYS", "7"))  # days

# MAIL CONFIG
MAIL_HOST = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "minhthuhuynh23@gmail.com"
MAIL_PASSWORD = "kapendjgusnxwczc"
MAIL_FROM = "ZY Banking <minhthuhuynh23@gmail.com>"
