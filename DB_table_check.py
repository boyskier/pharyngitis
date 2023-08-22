import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

def fetch_doctors():
    #query 수정해서 table 변경가능
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = "SELECT * FROM doctors;"
    cursor.execute(query)

    doctors = cursor.fetchall()
    for doctor in doctors:
        print(doctor)

    cursor.close()
    connection.close()

fetch_doctors()
