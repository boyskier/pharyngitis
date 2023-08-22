from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import mysql.connector
import bcrypt
from utils import *

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}

pharyngitis_model = tf.keras.models.load_model("D:\\User\\my_coding_projects\\pharyngitis_model.h5")
otoscope_model = tf.keras.models.load_model("D:\\User\\my_coding_projects\\otoscope_model.h5")

app = Flask(__name__)
secret_key = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = secret_key

@app.route('/') # endopint는 함수명인 main_page가 됨.
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
        image_size = (500, 500)
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

@app.route('/check_patients_page', methods=['GET'])
def check_patients_page():
    if 'doctor_user_name' not in session:  # 의사 정보가 세션에 없으면
        return redirect(url_for('doctor_signin_page'))  # 로그인 페이지로 리다이렉트

    return render_template('check_patients.html')


@app.route('/check_patients', methods=['POST'])
def check_patients():
    user_name = request.form.get('user_name')
    table_name = request.form.get('table_name')

    images = show_all_images_by_user_name_web(user_name, table_name)
    if not images:
        return "No records found for user " + user_name

    return render_template('patient_images.html', user_name=user_name, images=images)



if __name__ == '__main__':
    create_table('pharyngitis')
    create_table('otoscope')
    create_userinfo_table()
    create_doctors_table()
    app.run(debug=True)
