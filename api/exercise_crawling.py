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
        file_path = './api/megaGymDataset_db.csv'
        csv_data = read_csv_file(file_path)
        crawling(csv_data)
        return "크롤링 작업이 성공적으로 실행되었습니다."


def read_csv_file(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)
            for row in csv_reader:
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


def crawling(csv_data):
    connection = db_conn()
    # 읽어온 데이터 출력
    for row in csv_data:
        no = row[0]
        e_name = row[1]
        e_type = row[2]
        youtube_crawler = youtudeCrawling()
        youtube_result = youtube_crawler.get(e_name)
        youtube_url = youtube_result['href']
        video_id = re.search(r'(?<=v=)[^&]+', youtube_url).group(0)
        e_video_path = 'https://www.youtube.com/embed/' + video_id

        # wrtn_crawler = wrtnCrawling()
        # e_content = wrtn_crawler.get(e_name)

        print(f'index :{no} | e_name :{e_name} | e_type:{e_type} | e_video_path:{e_video_path}')

        insert_query = "INSERT INTO EXERCIES(e_name, e_type, e_video_path) VALUES (:e_name, :e_type, :e_video_path)"
        query_insert(connection, query=insert_query, e_name=e_name, e_type=e_type,e_video_path=e_video_path)
        print("insert 완료")
