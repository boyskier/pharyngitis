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
def connect_db():
    return mysql.connector.connect(**db_config)


def close_db(connection, cursor):
    cursor.close()
    connection.close()


def show_image(image_data, title=None):
    image_stream = io.BytesIO(image_data)
    image = Image.open(image_stream)
    plt.imshow(image)
    if title:
        plt.title(title)
    plt.axis('off')
    plt.show()


def get_image_data(image_id, table_name):
    connection = connect_db()
    cursor = connection.cursor()
    query = f"SELECT user_name, image_data, probability, upload_time FROM {table_name} WHERE id = {image_id};"
    cursor.execute(query)
    result = cursor.fetchone()
    close_db(connection, cursor)

    if result is None:
        print(f"No record found for image_id {image_id}")
        return None

    return result


def show_image_data_from_image_id(image_id, table_name):
    data = get_image_data(image_id, table_name)
    if data:
        user_name, image_data, probability, upload_time = data
        show_image(image_data)
        print(f"User Name: {user_name}")
        print(f"Upload Time: {upload_time}")
        print(probability)


def show_all_images_by_user_name(user_name, table_name):
    connection = connect_db()
    cursor = connection.cursor()
    query = f"SELECT image_data, upload_time, probability FROM {table_name} WHERE user_name = '{user_name}';"
    cursor.execute(query)
    results = cursor.fetchall()
    close_db(connection, cursor)

    if not results:
        print(f"No records found for user {user_name}")
        return None

    total_images = len(results)
    rows = 2
    cols = (total_images + rows - 1) // rows
    print(f"Total {table_name} images for user {user_name}: {total_images}")

    fig, axes = plt.subplots(rows, cols, figsize=(20, 10))  # 2행과 열의 수를 설정합니다.
    fig.subplots_adjust(wspace=0.5, hspace=0.5)  # 서브플롯 간 간격을 늘립니다.

    if rows == 1 or cols == 1:
        axes = axes.reshape(rows, cols)  # 1차원 배열인 경우, 형상을 바꿉니다.

    for i, (image_data, upload_time, probability) in enumerate(results):
        title = f"{user_name}_{upload_time.strftime('%Y%m%d_%H%M%S')}_{probability:.3f}"
        image_stream = io.BytesIO(image_data)
        image = Image.open(image_stream)

        ax = axes[i // cols, i % cols]
        ax.imshow(image)
        ax.set_title(title, fontsize=10)
        ax.axis('off')

    plt.show()


user_name = 'patient2'  # 원하는 환자 이름으로 수정
show_all_images_by_user_name(user_name, 'pharyngitis')
show_all_images_by_user_name(user_name, 'otoscope')
