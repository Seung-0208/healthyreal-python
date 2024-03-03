import os

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from flask_restful import Resource
from selenium.webdriver.common.keys import Keys
from basic_fuc import db_conn, query_insert, db_disconn, query_select
import csv
from wrtnai_crawling import wrtnCrawling
from youtude_crawling import youtudeCrawling
import re


# 유저가 검색하면 크롤링 후 DB에 저장하는 API
class exerciseCrawling(Resource):
    def get(self):
        print('들어왕ㅆ니?')
        file_path = './api/megaGymDataset_db3.csv'
        csv_data = read_csv_file(file_path)
        crawling(csv_data)
        return "크롤링 작업이 성공적으로 실행되었습니다."


def read_csv_file(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='euc-kr') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
                data.append(row)
    except UnicodeDecodeError:
        print("UnicodeDecodeError: 'utf-8' codec can't decode byte")
        print("Trying another encoding...")
        # 다른 인코딩 방식으로 재시도
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
                data.append(row)
    return data


def crawling(csv_data):
    connection = db_conn()

    error_list = []
    # 읽어온 데이터 출력
    for row in csv_data:
        no = row[0]
        e_name = row[1]
        # desc = row[2]
        e_type = row[2]
        youtube_crawler = youtudeCrawling()
        youtube_result = youtube_crawler.get(e_name)
        youtube_url = youtube_result['href']

        try:
            video_id = re.search(r'(?<=v=)[^&]+', youtube_url).group(0)
            e_video_path = 'https://www.youtube.com/embed/' + video_id
        except (AttributeError, KeyError) as e:
            # 만약 비디오 ID를 추출하거나 YouTube에서 결과를 얻지 못하면 해당 행을 에러 리스트에 추가하고 건너뜁니다.
            print(f"Failed to process row {no}: {e_name}")
            error_list.append(row)
            continue
        except Exception as e:
            # 다른 예외가 발생한 경우에도 처리합니다.
            print(f"Error processing row {no}: {e}")
            error_list.append(row)
            continue

        # e_content = papago_crawling(desc)

        # wrtn_crawler = wrtnCrawling()
        # e_content = wrtn_crawler.get(e_name)
        print(f'index :{no} | e_name :{e_name} | e_type:{e_type} | e_video_path:{e_video_path}')
        insert_query = "INSERT INTO EXERCIES(e_name, e_type, e_video_path) VALUES (:e_name, :e_type, :e_video_path)"
        query_insert(connection, query=insert_query, e_name=e_name, e_type=e_type,e_video_path=e_video_path)

        # print(f'index :{no} | e_name :{e_name} | e_type:{e_type} | e_video_path:{e_video_path} | e_content:{e_content}')

        # insert_query = "INSERT INTO EXERCIES(e_name, e_type, e_video_path,e_content) VALUES (:e_name, :e_type, :e_video_path,:e_content)"
        # query_insert(connection, query=insert_query, e_name=e_name, e_type=e_type,e_video_path=e_video_path, e_content=e_content)
        print("insert 완료")

    # error_list를 error_list.csv 파일로 저장합니다.
    save_error_list_to_csv(error_list)

def save_error_list_to_csv(error_list, filename='error_list.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['index', 'e_name', 'e_type'])
        writer.writerows(error_list)
def papago_crawling(desc):
    try:
        # 1.WebDriver객체 생성
        driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
        # 웹드라이버를 위한 Service객체 생성
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # headless 모드 설정
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")  # 사용자 에이전트 설정
        # 자동종료 막기
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=service, options=options)
        # 2.브라우저에 네이버 페이지 로딩하기
        driver.get('https://papago.naver.com/')
        time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        search_box = driver.find_element(By.XPATH,'//*[@id="txtSource"]')
        search_box.send_keys(desc)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        answer = driver.find_element(By.XPATH,'//*[@id="txtTarget"]/span')
        print(answer)
        print(answer.text)
        return answer.text


    finally:
        # # 가상 디스플레이 종료
        # display.stop()
        pass
