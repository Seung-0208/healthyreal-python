
from api.db_connection import connect_to_oracle

def db_conn():
    # 오라클 데이터베이스에 연결
    connection = connect_to_oracle()
    return connection
    print("데이터베이스에 연결했습니다.")

def query_insert(connection, query, **kwargs):
    # 커서 생성
    cursor = connection.cursor()
    cursor.execute(query, kwargs)

    # # 변경 사항 커밋
    connection.commit()
    print("데이터베이스 변경 사항을 커밋했습니다.")

    # 연결 종료
    cursor.close()

def query_select(connection, query, **kwargs):
    # 커서 생성
    cursor = connection.cursor()
    cursor.execute(query, kwargs)

    # 결과 가져오기
    result = cursor.fetchall()

    # 커서 닫기
    cursor.close()

    return result


def db_disconn(connection):
    connection.close()
    print("데이터베이스 연결을 종료했습니다.")