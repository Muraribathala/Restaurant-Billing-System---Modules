import mysql.connector
def connect_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="RestaurantBillingSystem"
        )
        return conn
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None