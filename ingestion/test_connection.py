import psycopg2
import os
from getpass import getpass

# Database connection details
DB_NAME = "customer_churn_db"
DB_USER = "postgres"
DB_HOST = "localhost"
DB_PORT = "5432"

# Ask for password securely
DB_PASSWORD = getpass("Enter PostgreSQL password: ")

try:
    connection = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = connection.cursor()

    cursor.execute("SELECT current_database(), current_user;")
    result = cursor.fetchone()

    print("Database connection successful!")
    print("Database:", result[0])
    print("User:", result[1])

    cursor.close()
    connection.close()

except psycopg2.Error as error:
    print("Database connection failed!")
    print(error)