import pymysql

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="zybank",
        cursorclass=pymysql.cursors.DictCursor  # rất quan trọng
    )
