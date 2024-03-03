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

class wrtnCrawling(Resource):
    def post(self, search):
        # search = request.json['search']
        result = driver_crawling(search)
        return result
    def get(self, search):
        result = driver_crawling(search)
        return result

    # def get(self):
    #     search = request.args.get('search')
    #     # id = request.args.get('id')
    #     result = driver_crawling(search)
    #     return result


def driver_crawling(search):
    result = []  # 결과를 저장할 리스트
    try:
        # 1.WebDriver객체 생성
        driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
        # 웹드라이버를 위한 Service객체 생성
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # headless 모드 설정
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")  # 사용자 에이전트 설정
        # 자동종료 막기
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=service, options=options)
        # 2.브라우저에 네이버 페이지 로딩하기
        driver.get('https://wrtn.ai/')
        time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        # gpt3_5  = driver.find_element(By.XPATH, '//*[@id="__main"]/main/div/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[3]')
        # print(gpt3_5)
        # gpt3_5.click()

        search_box = driver.find_element(By.XPATH, '//*[@id="__main"]/main/div/div[2]/div/div/div/div/div[3]/div/div[4]/textarea')
        print(search_box)

        search_box.send_keys(search)
        # Enter 키 전송
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)
        wait = WebDriverWait(driver, 30)
        # answer = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ScrollContainer"]/div[1]/div/div/div[3]/div/div[2]/swiper-container/swiper-slide/div/div[1]/div[1]/div/p')))

        search_box.send_keys(search)
        # Enter 키 전송
        search_box.send_keys(Keys.RETURN)
        time.sleep(10)
        wait = WebDriverWait(driver, 30)
        # answer = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ScrollContainer"]/div[1]/div/div/div[3]/div/div[2]/swiper-container/swiper-slide/div/div[1]/div[1]/div/p')))
        answer = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ScrollContainer"]/div[1]/div/div/div[5]/div/div[2]/swiper-container/swiper-slide/div/div[1]/div[1]/div/ol')))

        # print(answer)
        print('뤼튼 답변 :',answer.text)
        return answer.text


    except (TimeoutException, NoSuchElementException) as e:
        print('지정한 요소를 찾을수 없어요:', e)
    finally:
        driver.quit()
    return result