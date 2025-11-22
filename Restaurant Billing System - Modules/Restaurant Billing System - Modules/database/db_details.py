import mysql.connector
def connect_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="your db username",
            password="your db password",
            database="your db name"
        )
        return conn
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None