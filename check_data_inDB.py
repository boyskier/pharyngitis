import mysql.connector
from PIL import Image
import io
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}



# image_id로 부터 정보 확인
def get_image_data(image_id, table_name): #table_name: pharyngitis, otoscope
    # DB 연결
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 이미지 데이터 불러오기
    query = f"SELECT user_name, image_data, probability, upload_time FROM {table_name} WHERE id = {image_id};"  # 원하는 id 사용
    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result is None:
        print(f"No record found for image_id {image_id}")
        return None

    return result

def show_image_data_from_image_id(image_id, table_name): #table_name: pharyngitis, otoscope
    user_name, image_data, probability, upload_time = get_image_data(image_id, table_name)

    # 바이트 스트림으로 이미지 열기
    image_stream = io.BytesIO(image_data)
    image = Image.open(image_stream)

    # 이미지 출력
    image.show()

    print(f"User Name: {user_name}")
    print(f"Upload Time: {upload_time}")
    print(probability)

# 환자명을 받아서 모든 이미지 출력


def show_all_images_by_user_name(user_name, table_name): #table_name: pharyngitis, otoscope
    # DB 연결
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 환자 이름으로 이미지 데이터 불러오기
    query = f"SELECT image_data, upload_time, probability FROM {table_name} WHERE user_name = '{user_name}';"
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()

    if not results:
        print(f"No records found for user {user_name}")
        return None

        # 전체 이미지 수 출력
    total_images = len(results)
    print(f"Total images for user {user_name}: {total_images}")

    for image_data, upload_time, probability in results:
        # 바이트 스트림으로 이미지 열기
        image_stream = io.BytesIO(image_data)
        image = Image.open(image_stream)

        # 제목 설정
        title = f"{user_name}_{upload_time.strftime('%Y%m%d_%H%M%S')}_{probability:.3f}"

        # 이미지 출력
        plt.imshow(image)
        plt.title(title)
        plt.axis('off') # 축을 제거하여 이미지만 표시
        plt.show()

        print(f"Upload Time: {upload_time}")
        print(f"Probability: {probability}")

user_name = 'patient2'  # 원하는 환자 이름으로 수정
show_all_images_by_user_name(user_name, 'otoscope')
