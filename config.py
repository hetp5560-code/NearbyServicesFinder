import pymysql

connection = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="nearby_services_finder",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False
)