import os

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from flask import request
from flask_restful import Resource
from selenium.webdriver.common.keys import Keys
from basic_fuc import db_conn, query_insert, db_disconn, query_select
import csv
class ttest(Resource):
    def post(self, search):
        # search = request.json['search']
        return 'dk'
    # def get(self, search):
    #     result = driver_crawling(search)
    #     return result

    # def get(self):
    #     connection = db_conn()
    #     select_query = "SELECT E_NAME,E_CONTENT FROM EXERCIES"
    #     select_result = query_select(connection, query=select_query)
    #     print("조회된 행 : ",select_result)
    #
    #     if select_result:
    #         print("[크롤링 시작]")
    #         for E_NAME, E_CONTENT in select_result:
    #             print("이번 크롤링 운동 : ", E_NAME)
    #             result = driver_crawling(E_NAME)
    #             update_query = "UPDATE EXERCIES SET E_CONTENT = :E_CONTENT WHERE E_NAME = :E_NAME"
    #             query_insert(connection, query=update_query, E_NAME= E_NAME,E_CONTENT=result)
    #             print("update 결과 :",update_query)
    #
    #     db_disconn(connection)
    #     return "크롤링 완료"

    def get(self):
        file_path = './api/exercise_leejh.csv'
        csv_data = read_csv_file(file_path)
        DBinsert(csv_data)
        return "DB 작업이 성공적으로 실행되었습니다."

def read_csv_file(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                next(csv_reader)
                data.append(row)
    except UnicodeDecodeError:
        print("UnicodeDecodeError: 'utf-8' codec can't decode byte")
        print("Trying another encoding...")
        # 다른 인코딩 방식으로 재시도
        with open(file_path, newline='', encoding='euc-kr') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
                data.append(row)
    return data

def DBinsert(csv_data):
    connection = db_conn()
    # 읽어온 데이터 출력
    for row in csv_data:
        e_name = row[0]
        e_content = row[3]
        calories_per_hour = row[5]

        print(f'운동명 : {e_name} | 설명 : {e_content} | 시간당 칼로리 : {calories_per_hour}')

        update_query = "UPDATE exercies SET e_content = :e_content, calories_per_hour=:calories_per_hour  WHERE e_name = :e_name"
        query_insert(connection, query=update_query, e_name=e_name, e_content=e_content, calories_per_hour=calories_per_hour)
        print("업데이트 완료")

    db_disconn(connection)

# def driver_crawling(search):
#     result = []  # 결과를 저장할 리스트
#     try:
#         # 1.WebDriver객체 생성
#         driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
#         # 웹드라이버를 위한 Service객체 생성
#         service = Service(executable_path=driver_path)
#         options = webdriver.ChromeOptions()
#         # options.add_argument("--headless")  # headless 모드 설정
#         options.add_argument(
#             "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")  # 사용자 에이전트 설정
#         # 자동종료 막기
#         options.add_experimental_option("detach", True)
#         driver = webdriver.Chrome(service=service, options=options)
#         # 2.브라우저에 네이버 페이지 로딩하기
#         driver.get('https://wrtn.ai/')
#         time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림
#
#         # gpt3_5  = driver.find_element(By.XPATH, '//*[@id="__main"]/main/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]')
#         # print(gpt3_5)
#         # gpt3_5.click()
#
#         search_box = driver.find_element(By.XPATH, '//*[@id="__main"]/main/div/div[2]/div/div/div/div/div[3]/div/div[4]/textarea')
#         print(search_box)
#
#         search_box.send_keys(search+'의 시간당 소비 칼로리는?')
#         # Enter 키 전송
#         search_box.send_keys(Keys.RETURN)
#         time.sleep(10)
#         wait = WebDriverWait(driver, 30)
#         answer0 = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ScrollContainer"]/div[1]/div/div/div[3]/div/div[2]/swiper-container/swiper-slide/div/div[1]/div[1]/div/p')))
#         print('시간 당 소비 칼로리 : ',answer0.text)
#
#         search_box.send_keys(search)
#         # Enter 키 전송
#         search_box.send_keys(Keys.RETURN)
#         time.sleep(10)
#         wait = WebDriverWait(driver, 30)
#         # answer = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ScrollContainer"]/div[1]/div/div/div[3]/div/div[2]/swiper-container/swiper-slide/div/div[1]/div[1]/div/p')))
#         answer = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ScrollContainer"]/div[1]/div/div/div[5]/div/div[2]/swiper-container/swiper-slide/div/div[1]/div[1]/div/ol')))
#
#         # print(answer)
#         print('뤼튼 답변 :',answer.text)
#         return answer.text
#
#
#     except (TimeoutException, NoSuchElementException) as e:
#         print('지정한 요소를 찾을수 없어요:', e)
#     finally:
#         driver.quit()
#     return result
########################################################################################################