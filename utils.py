from keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import tensorflow as tf
import io
import mysql.connector
from dotenv import load_dotenv
import os
import base64
import torch
import torchvision.transforms as transforms
from PIL import Image
import io

load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}


def connect_db():
    return mysql.connector.connect(**db_config)


def close_db(connection, cursor):
    cursor.close()
    connection.close()


def create_userinfo_table():
    '''
    Creates the userinfo table in the database.
    user_name: user_name
    password: password
    birth_date: YYYYMMDD
    gender: 0 = female, 1 = male
    '''

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = f"""
    CREATE TABLE IF NOT EXISTS userinfo (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        birth_date VARCHAR(8),
        gender INT
    );
    """

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def create_doctors_table():  # doctors라는 table에 의사 정보 저장

    # license: 의사 면허번호

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = f"""
    CREATE TABLE IF NOT EXISTS doctors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(255) UNIQUE,
        password VARCHAR(255),
        licence VARCHAR(8)
    );
    """

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def create_table(table_name):  # table_name: pharyngitis, otoscope
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(255),
        image_data MEDIUMBLOB,
        probability DOUBLE,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def create_patient_doctor_table():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = '''
        CREATE TABLE IF NOT EXISTS patient_doctor (
            patient_id VARCHAR(50),
            doctor_id VARCHAR(50)
        );
    '''
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def save_image_to_db(user_name, image_data, probability, table_name):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = f"""
    INSERT INTO {table_name} (user_name, image_data, probability) VALUES (%s, %s, %s);
    """
    cursor.execute(query, (user_name, image_data, probability))
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Image from user {user_name} with probability {probability} has been saved to the database.")


# def show_all_images_by_user_name_web(user_name, table_name):
#     connection = connect_db()
#     cursor = connection.cursor()
#     query = f"SELECT image_data, upload_time, probability FROM {table_name} WHERE user_name = '{user_name}';"
#     cursor.execute(query)
#     results = cursor.fetchall()
#     close_db(connection, cursor)
#
#     if not results:
#         return None
#
#     images = []
#     for image_data, upload_time, probability in results:
#         image_base64 = base64.b64encode(image_data).decode('utf-8')
#         images.append((image_base64, upload_time, probability))
#
#     return images

def show_all_images_by_user_name_web(user_name, table_name, page, items_per_page):
    start_index = (page - 1) * items_per_page
    connection = connect_db()
    cursor = connection.cursor()
    query = f"""SELECT image_data, upload_time, probability 
                FROM {table_name} 
                WHERE user_name = '{user_name}' 
                LIMIT {start_index}, {items_per_page};"""
    cursor.execute(query)
    results = cursor.fetchall()
    close_db(connection, cursor)

    if not results:
        return None

    images = []
    for image_data, upload_time, probability in results:
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        images.append((image_base64, upload_time, probability))

    return images


def show_all_images_by_user_name_web_paged(user_name, table_name, page, items_per_page):
    offset = (page - 1) * items_per_page  # 이름을 'offset'으로 변경하였습니다.
    connection = connect_db()
    cursor = connection.cursor()
    # print(f"offset: {offset}")
    query = f"""SELECT image_data, upload_time, probability 
                    FROM {table_name} 
                    WHERE user_name = '{user_name}' 
                    LIMIT {offset}, {items_per_page};"""
    cursor.execute(query)

    results = cursor.fetchall()
    close_db(connection, cursor)

    if not results:
        return None

    images = []
    for image_data, upload_time, probability in results:
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        images.append((image_base64, upload_time, probability))

    return images
