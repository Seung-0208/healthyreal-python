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
import json

class youtudeCrawling(Resource):
    def get(self):
        search = request.args.get('search')
        if search is None:
            return {'message': '검색어를 전달해주세요.'}, 400  # 검색어가 전달되지 않았을 때의 예외 처리

        print('전달받은 값:', search)
        result = youtude_crawling(search)
        return result
        # youtude_crawling(search)
        # return "성공?"

    # ## exercise_crawling과 연결 버전
    # def get(self, e_name):
    #
    #     print('전달받은 값:', e_name)
    #     result = youtude_crawling(e_name)
    #     return result

def youtude_crawling(search):
    print('유튜브 크롤링을 시작합니다.')

    try:
        # 1.WebDriver객체 생성
        driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
        # 웹드라이버를 위한 Service객체 생성
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # headless 모드 설정
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")  # 사용자 에이전트 설정
        # 자동종료 막기
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=service, options=options)
        # 2.브라우저에 네이버 페이지 로딩하기
        driver.get('https://www.youtube.com/')
        time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        search_box = driver.find_element(By.XPATH,'//*[@id="search-input"]/input')

        search_box.send_keys(search)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        video = driver.find_element(By.XPATH,'//*[@id="contents"]/ytd-video-renderer[2]/div[1]')

        title = driver.find_element(By.XPATH,'//*[@id="video-title"]/yt-formatted-string').text
        print('제목',title)
        a_tag = video.find_element(By.XPATH,'./ytd-thumbnail/a')
        href = a_tag.get_attribute('href')
        print('링크', href)
        img = a_tag.find_element(By.XPATH, './yt-image/img')
        src = img.get_attribute('src')
        print('img', img)
        print('src', src)

        result = {
            'title' : title,
            'href' : href,
            'src' : src
        }

        return result
    finally:
        # # 가상 디스플레이 종료
        # display.stop()
        pass
