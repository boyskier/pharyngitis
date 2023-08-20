from flask import Flask, request, send_file
from keras.preprocessing.image import img_to_array, load_img
import numpy as np
import tensorflow as tf
import io
from PIL import Image
import mysql.connector
from flask import jsonify
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

def create_table(): #images라는 테이블을 생성
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS images (
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

def save_image_to_db(user_name, image_data, probability):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = """
    INSERT INTO images (user_name, image_data, probability) VALUES (%s, %s, %s);
    """
    cursor.execute(query, (user_name, image_data, probability))

    connection.commit()
    cursor.close()
    connection.close()
    print(f"Image from user {user_name} with probability {probability} has been saved to the database.")


app = Flask(__name__)

model_path = "D:\\User\\my_coding_projects\\my_model.h5"
model = tf.keras.models.load_model(model_path)

#temp_image에 저장하는 방식
'''
@app.route('/upload', methods=['POST'])
def upload_image():
    uploaded_file = request.files['file']
    user_name = request.form['user_name']

    if uploaded_file.filename != '':
        # 이미지 파일을 임시 경로에 저장
        image_path = "temp_image.jpg"
        uploaded_file.save(image_path)

        # 이미지를 모델에 입력할 수 있는 형태로 전처리
        image = load_img(image_path, target_size=(224, 224))
        image_array = img_to_array(image)
        image_array = tf.keras.applications.resnet.preprocess_input(image_array)
        image_array = np.expand_dims(image_array, axis=0)

        # 예측 수행
        prediction = model.predict(image_array)
        probability = prediction[0][0]

        # 확률 값을 일반 float로 변환
        if isinstance(probability, np.float32):
            probability = float(probability)

        # 이미지를 바이트 스트림으로 변환
        image = Image.open(image_path)
        byte_stream = io.BytesIO()
        image.save(byte_stream, format='JPEG')
        byte_stream.seek(0)
        image_data = byte_stream.read()

        save_image_to_db(user_name, image_data, probability) # DB에 이미지와 사용자 정보 저장

        # 응답에 이미지와 확률 값을 같이 반환
        response_data = {
            'probability': probability,
            'image': base64.b64encode(image_data).decode()
        }

        return jsonify(response_data)
    else:
        return {'error': 'No file uploaded'}
'''

#memory에 직접 저장하는 방식
@app.route('/upload', methods=['POST'])
def upload_image():
    uploaded_file = request.files['file']
    user_name = request.form['user_name']

    if uploaded_file.filename != '':
        # 이미지 파일을 바이트 스트림으로 읽기
        byte_stream = io.BytesIO(uploaded_file.read())

        # 이미지를 PIL 객체로 로드
        image = Image.open(byte_stream)

        # 이미지를 모델에 입력할 수 있는 형태로 전처리
        image = image.resize((224, 224))
        image_array = img_to_array(image)
        image_array = tf.keras.applications.resnet.preprocess_input(image_array)
        image_array = np.expand_dims(image_array, axis=0)

        # 예측 수행
        prediction = model.predict(image_array)
        probability = prediction[0][0]

        # 확률 값을 일반 float로 변환
        if isinstance(probability, np.float32):
            probability = float(probability)

        # 이미지를 바이트 스트림으로 다시 변환 (필요한 경우)
        byte_stream.seek(0)
        image_data = byte_stream.read()

        save_image_to_db(user_name, image_data, probability) # DB에 이미지와 사용자 정보 저장

        # 응답에 이미지와 확률 값을 같이 반환
        response_data = {
            'probability': probability,
            'image': base64.b64encode(image_data).decode()
        }

        return jsonify(response_data)
    else:
        return {'error': 'No file uploaded'}



if __name__ == '__main__':
    create_table() # 테이블 생성
    app.run()


# just for check