from flask import Flask, request, jsonify
from keras.preprocessing.image import img_to_array
from PIL import Image
import numpy as np
import tensorflow as tf
import io
import mysql.connector
import base64
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

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


def create_table(table_name): #table_name: pharyngitis, otoscope
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


pharyngitis_model = tf.keras.models.load_model("D:\\User\\my_coding_projects\\pharyngitis_model.h5")
otoscope_model = tf.keras.models.load_model("D:\\User\\my_coding_projects\\otoscope_model.h5")

app = Flask(__name__)

def process_image(uploaded_file, model, image_size):
    byte_stream = io.BytesIO(uploaded_file.read())
    image = Image.open(byte_stream)
    image = image.resize(image_size)
    image_array = img_to_array(image)
    image_array = tf.keras.applications.resnet.preprocess_input(image_array)
    image_array = np.expand_dims(image_array, axis=0)
    prediction = model.predict(image_array)
    probability = float(prediction[0][0])
    byte_stream.seek(0)
    image_data = byte_stream.read()
    return probability, image_data

@app.route('/signup', methods=['POST']) #회원가입 페이지
def signup():
    # 클라이언트로부터 정보 받기
    user_name = request.json.get('user_name')
    password = request.json.get('password')
    birth_date = request.json.get('birth_date')
    gender = request.json.get('gender') #1:male, 0:female

    # 사용자 ID 중복 확인
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"SELECT user_name FROM userinfo WHERE user_name = %s", (user_name,))
    result = cursor.fetchone()

    if result:
        connection.close()
        return jsonify({'status': 'error', 'message': 'User ID already exists'})

    # 사용자 정보 저장
    query = f"""
    INSERT INTO userinfo (user_name, password, birth_date, gender) VALUES (%s, %s, %s, %s);
    """
    cursor.execute(query, (user_name, password, birth_date, gender))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/signin', methods=['POST'])
def signin():
    user_name = request.json.get('user_name')
    password = request.json.get('password')

    # 데이터베이스에서 사용자 정보 조회
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"SELECT password FROM userinfo WHERE user_name = %s", (user_name,))
    result = cursor.fetchone()
    connection.close()

    # ID와 비밀번호 검증
    if result and result[0] == password:
        return jsonify({'status': 1})  # 인증 성공
    else:
        return jsonify({'status': 0})  # 인증 실패



@app.route('/upload/<table_name>', methods=['POST'])
def upload_image(table_name):
    uploaded_file = request.files['file']
    user_name = request.form['user_name']

    if table_name == 'pharyngitis':
        image_size = (224,224)
        model = pharyngitis_model
    else:
        image_size = (500,500)
        model = otoscope_model


    if uploaded_file.filename != '':
        probability, image_data = process_image(uploaded_file, model, image_size)
        save_image_to_db(user_name, image_data, probability, table_name)
        response_data = {
            'probability': probability,
            'image': base64.b64encode(image_data).decode()
        }
        return jsonify(response_data)
    else:
        return {'error': 'No file uploaded'}

if __name__ == '__main__':
    create_table('pharyngitis')
    create_table('otoscope')
    create_userinfo_table()
    app.run()

