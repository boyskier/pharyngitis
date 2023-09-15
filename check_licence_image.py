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


def approve_doctor():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT id, user_name, licence, permission FROM doctors WHERE permission = 0;"
    cursor.execute(query)
    doctors_to_approve = cursor.fetchall()  # Fetch all rows

    for doctor in doctors_to_approve:
        print(f"ID: {doctor['id']}, Username: {doctor['user_name']}, current permission: {doctor['permission']}")

    while True:
        selected_id = int(input("Enter the ID of the doctor to approve or disapprove: "))

        try:
            # plot the licence image
            query = "SELECT licence FROM doctors WHERE id = %s;"
            cursor.execute(query, (selected_id,))
            licence = cursor.fetchone()['licence']
            licence_decoded = base64.b64decode(licence)

            image = Image.open(io.BytesIO(licence_decoded))
            image.show()
            new_permission = int(input("Enter new permission (1 for approve, -1 for disapprove): "))

            if new_permission not in [-1, 0, 1]:
                print("Invalid Input")
                break

            query = "UPDATE doctors SET permission = %s WHERE id = %s;"
            cursor.execute(query, (new_permission, selected_id))
            connection.commit()
        except:
            print('invalid licence image')

    cursor.close()
    connection.close()

if __name__ == '__main__':
    print('app')
    approve_doctor()

# if not os.path.exists('DB_image_data/licence'):
#     os.makedirs('DB_image_data/licence')
# # get licence image and plot
# for i, (user_name, licence) in enumerate(all_results):
#     file_name = f"licence_{user_name}_{i}.jpg"
#     file_path = os.path.join(f'DB_image_data/licence', file_name)
#     try:
#         licence_decoded = base64.b64decode(licence)
#
#         image = Image.open(io.BytesIO(licence_decoded))
#         image.save(file_path)
#         print(f"Image saved at {file_path}")
#     except:
#         print(f"Image not saved at {file_path}")
