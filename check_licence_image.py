import mysql.connector
from PIL import Image
import io
from dotenv import load_dotenv
import os
import base64

load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

query = f"""SELECT user_name, licence FROM doctors WHERE permission = 0;"""
cursor.execute(query)


all_results = cursor.fetchall()  # 모든 결과를 가져옴

if not os.path.exists('DB_image_data/licence'):
    os.makedirs('DB_image_data/licence')
# get licence image and plot
for i, (user_name, licence) in enumerate(all_results):
    file_name = f"licence_{user_name}_{i}.jpg"
    file_path = os.path.join(f'DB_image_data/licence', file_name)
    try:
        licence_decoded = base64.b64decode(licence)

        image = Image.open(io.BytesIO(licence_decoded))
        image.save(file_path)
        print(f"Image saved at {file_path}")
    except:
        print(f"Image not saved at {file_path}")
