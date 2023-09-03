from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
import bcrypt
from utils import *
from waitress import serve
from PIL import Image

import torch
from Fever_pytorch_structure_2 import CustomModel, HuggingfaceCustomModel, IdentityLayer

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

# tf model
# pharyngitis_model = tf.keras.models.load_model("pharyngitis_model.h5")
# otoscope_model = tf.keras.models.load_model("otoscope_model.h5")

pharyngitis_model = torch.load("google_vit-base-patch16-224_model.pth", map_location=torch.device('cpu'))


# otoscope_model = torch.load("alexnet_model.pth")

def process_image(uploaded_file, model, image_size):
    model.to("cpu")
    model.eval()
    byte_stream = io.BytesIO(uploaded_file.read())
    image = Image.open(byte_stream)
    image = model.transformer(image)
    image = image.unsqueeze(dim=0)  # Add a batch dimension
    output = model(image)

    probability = float(model.prob_func(output))
    # print(probability)
    # print(type(probability))
    # Go back to the start of the byte stream to read the image data
    byte_stream.seek(0)
    image_data = byte_stream.read()

    return probability, image_data


app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = secret_key


@app.route('/')  # endopint는 함수명인 main_page가 됨.
def main_page():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])  # 회원가입 페이지
def signup():
    # 클라이언트로부터 정보 받기
    user_name = request.json.get('user_name')
    password = request.json.get('password').encode('utf-8')  # 인코딩
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())  # 해싱
    birth_date = request.json.get('birth_date')
    gender = request.json.get('gender')  # 1:male, 0:female

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
    cursor.execute(query, (user_name, hashed_password, birth_date, gender))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'success', 'message': 'User registered successfully'})


@app.route('/signin', methods=['POST'])
def signin():
    user_name = request.json.get('user_name')
    password = request.json.get('password').encode('utf-8')  # 인코딩

    # 데이터베이스에서 사용자 정보 조회
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"SELECT password FROM userinfo WHERE user_name = %s", (user_name,))
    result = cursor.fetchone()
    connection.close()

    # ID와 비밀번호 검증 (해싱된 비밀번호와 비교)
    if result and bcrypt.checkpw(password, result[0].encode('utf-8')):
        return jsonify({'status': 1})  # 인증 성공
    else:
        return jsonify({'status': 0})  # 인증 실패


@app.route('/doctor_signup_page', methods=['GET'])
def doctor_signup_page():
    return render_template('doctor_signup.html')


@app.route('/doctor_signup', methods=['POST'])  # 의사 회원가입 페이지
def doctor_signup():
    # 클라이언트로부터 정보 받기
    user_name = request.form.get('user_name')
    password = request.form['password'].encode('utf-8')  # 인코딩
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())  # 해싱
    licence = request.form['licence']

    # 의사 ID 중복 확인
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"SELECT user_name FROM doctors WHERE user_name = %s", (user_name,))
    result = cursor.fetchone()

    if result:
        connection.close()
        return jsonify({'status': 'error', 'message': 'User ID already exists'})

    # 의사 정보 저장
    query = f"""
        INSERT INTO doctors (user_name, password, licence) VALUES (%s, %s, %s);
        """
    cursor.execute(query, (user_name, hashed_password, licence))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'status': 'success', 'message': 'Doctor registered successfully'})


@app.route('/doctor_signin_page', methods=['GET'])
def doctor_signin_page():
    return render_template('doctor_signin.html')


@app.route('/doctor_signin', methods=['POST'])
def doctor_signin():
    user_name = request.form.get('user_name')
    password = request.form['password'].encode('utf-8')  # 인코딩

    # 데이터베이스에서 의사 정보 조회
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"SELECT password FROM doctors WHERE user_name = %s", (user_name,))
    result = cursor.fetchone()
    connection.close()

    # ID와 비밀번호 검증 (해싱된 비밀번호와 비교)
    if result and bcrypt.checkpw(password, result[0].encode('utf-8')):
        session['doctor_user_name'] = user_name  # 세션에 의사 정보 저장
        return redirect(url_for('check_patients_page'))
    else:
        return jsonify({'status': 'error', 'message': 'Authentication failed'})


@app.route('/upload/<table_name>', methods=['POST'])
def upload_image(table_name):
    uploaded_file = request.files['file']
    user_name = request.form['user_name']

    if table_name == 'pharyngitis':
        image_size = (224, 224)
        model = pharyngitis_model
    else:
        image_size = (224, 224)
        # model = otoscope_model

    if uploaded_file.filename != '':
        probability, image_data = process_image(uploaded_file, model,
                                                image_size)  # Assuming process_image is adapted for PyTorch
        save_image_to_db(user_name, image_data, probability,
                         table_name)  # Assuming this function doesn't need to be modified
        response_data = {
            'probability': probability,
            'image': base64.b64encode(image_data).decode()
        }
        return jsonify(response_data)
    else:
        return {'error': 'No file uploaded'}


@app.route('/check_patients_page', methods=['GET'])
def check_patients_page():
    if 'doctor_user_name' not in session:  # 의사 정보가 세션에 없으면
        return redirect(url_for('doctor_signin_page'))  # 로그인 페이지로 리다이렉트

    return render_template('select_patients.html')


@app.route('/check_patients', methods=['POST'])
def check_patients():
    user_name = request.form.get('patient_id')
    table_name = request.form.get('table_name')
    # page = int(request.form.get('page', 1))  # 페이지 번호, 기본은 1
    page = 1
    items_per_page = 6  # 페이지 당 아이템 개수, 이 값을 변경할 수 있습니다.
    doctor_id = session.get('doctor_user_name')

    try:
        # Check if doctor has permission
        with mysql.connector.connect(**db_config) as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM patient_doctor WHERE patient_id = %s AND doctor_id = %s;"
            cursor.execute(query, (user_name, doctor_id))
            permission_result = cursor.fetchone()

            if not permission_result:
                return "You don't have permission to access this patient's records."

        images = show_all_images_by_user_name_web(user_name, table_name, page, items_per_page)

        if not images:
            return "No records found for user " + user_name

        return render_template('patient_images.html', user_name=user_name, images=images, current_page=page,
                               table_name=table_name, items_per_page=items_per_page)

    except mysql.connector.Error as err:
        print("An error occurred:", err)
        return "An error occurred while processing your request."


@app.route('/check_patients_paged', methods=['GET'])
def check_patients_paged():
    user_name = request.args.get('user_name')
    table_name = request.args.get('table_name')
    # print('table_name', table_name)
    page = int(request.args.get('page', 1))
    # print('check_patients_paged:', user_name, table_name, page)
    items_per_page = 6  # 예시: 페이지 당 5개의 이미지

    images = show_all_images_by_user_name_web_paged(user_name, table_name, page, items_per_page)

    if not images:
        return "No records found for user " + user_name

    return render_template('patient_images.html', user_name=user_name, images=images, current_page=page,
                           table_name=table_name, items_per_page=items_per_page)


@app.route('/give_doctor_permission', methods=['POST'])
def give_doctor_permission():
    patient_id = request.json.get('patient_id')  # 1,2,3이런거 말고 patient1이런거
    doctor_id = request.json.get('doctor_id')  # 정확히는 username 입니다.

    # Check if doctor_id exists in doctors table
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT user_name FROM doctors WHERE user_name = %s;"
    cursor.execute(query, (doctor_id,))
    result = cursor.fetchone()

    if result:
        # Store in database
        query = '''
            INSERT INTO patient_doctor (patient_id, doctor_id) VALUES (%s, %s);
        '''
        cursor.execute(query, (patient_id, doctor_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'status': 'success', 'message': 'Doctor permission granted'})
    else:
        cursor.close()
        connection.close()
        return jsonify({'status': 'error', 'message': 'Doctor ID does not exist'})


if __name__ == '__main__':
    create_table('pharyngitis')
    create_table('otoscope')
    create_userinfo_table()
    create_doctors_table()
    create_patient_doctor_table()
    # serve(app, host='0.0.0.0', port=5000)
    app.run(debug=True)
