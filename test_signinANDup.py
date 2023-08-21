# signup, signin testcode

import requests

# 5명의 사용자 정보
users = [
    {'user_name': 'user1', 'password': 'pass1', 'birth_date': '19900101', 'gender': 1},
    {'user_name': 'user2', 'password': 'pass2', 'birth_date': '19900202', 'gender': 0},
    {'user_name': 'user3', 'password': 'pass3', 'birth_date': '19900303', 'gender': 1},
    {'user_name': 'user4', 'password': 'pass4', 'birth_date': '19900404', 'gender': 0},
    {'user_name': 'user5', 'password': 'pass5', 'birth_date': '19900505', 'gender': 1},
]

# 5명의 사용자 회원가입
for user in users:
    response = requests.post('http://127.0.0.1:5000/signup', json=user)
    print('Signup Response:', response.json())

# 6번째 사용자 (중복된 ID 사용)
duplicate_user = {
    'user_name': 'user1',  # 이미 등록된 ID
    'password': 'pass6',
    'birth_date': '19900606',
    'gender': 1
}
response = requests.post('http://127.0.0.1:5000/signup', json=duplicate_user)
print('Signup Response for duplicate user:', response.json())


# 로그인 실험: 이미 등록된 사용자
existing_user_login = {
    'user_name': 'user1',
    'password': 'pass1'
}
response = requests.post('http://127.0.0.1:5000/signin', json=existing_user_login)
print('Signin Response for existing user:', response.json())

# 로그인 실험: 데이터베이스에 없는 사용자
non_existing_user_login = {
    'user_name': 'userX',
    'password': 'passX'
}
response = requests.post('http://127.0.0.1:5000/signin', json=non_existing_user_login)
print('Signin Response for non-existing user:', response.json())
