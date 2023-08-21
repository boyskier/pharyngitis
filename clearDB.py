import mysql.connector
from dotenv import load_dotenv
import os

# 환경 변수 불러오기
load_dotenv()

db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE')
}


def clearDB():
    confirmation = input("정말로 모든 데이터베이스 테이블을 삭제하시겠습니까? \n삭제하시려면 clear_all_db를 입력하세요\n입력: ")
    if confirmation != 'clear_all_db':
        print("테이블 삭제가 취소되었습니다.")
        return

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # 테이블 목록을 얻기 위한 쿼리
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # 각 테이블을 순회하면서 삭제
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE {table_name}")
        print(f"{table_name} 테이블이 삭제되었습니다.")

    connection.commit()
    cursor.close()
    connection.close()
    print("모든 테이블이 삭제되었습니다.")


if __name__ == "__main__":
    clearDB()
