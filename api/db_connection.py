import cx_Oracle

def connect_to_oracle():
    # 데이터베이스 연결 설정
    connection = cx_Oracle.connect(
        user="TEAM",
        password="TEAM",
        dsn="192.168.0.8/XEPDB1"
    )

    # 연결 확인
    if connection:
        print("오라클 데이터베이스에 성공적으로 연결되었습니다.")

    # 연결 반환
    return connection
