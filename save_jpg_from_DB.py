import mysql.connector
from PIL import Image
import io
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

if not os.path.exists('DB_image_data/pharyngitis'):
    os.makedirs('DB_image_data/pharyngitis')
if not os.path.exists('DB_image_data/otoscope'):
    os.makedirs('DB_image_data/otoscope')


def save_images_as_jpg(table_name):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    query = f"SELECT user_name, image_data FROM {table_name};"
    cursor.execute(query)

    all_results = cursor.fetchall()  # 모든 결과를 가져옴

    for i, (user_name, image_data) in enumerate(all_results):
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"{table_name}_{current_time}_{user_name}_{i}.jpg"
        file_path = os.path.join(f'DB_image_data/{table_name}', file_name)
        image = Image.open(io.BytesIO(image_data))
        image.save(file_path)
        print(f"Image saved at {file_path}")

    cursor.close()
    connection.close()


# 함수 호출
save_images_as_jpg('pharyngitis')
