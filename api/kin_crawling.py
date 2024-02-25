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
import json

class kinCrawling(Resource):
    def post(self):
        search = request.json['search']
        print('검색어 : ', search)
        return driver_crawling(search)
    def get(self):
        search = request.args.get('search')
        # id = request.args.get('id')
        result = driver_crawling(search)
        return result




def driver_crawling(search):
    result = []  # 결과를 저장할 리스트
    try:
        # 1.WebDriver객체 생성
        driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
        # 웹드라이버를 위한 Service객체 생성
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # headless 모드 설정
        # 자동종료 막기
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=service, options=options)
        # 2.브라우저에 네이버 페이지 로딩하기
        driver.get('https://kin.naver.com/')
        wait = WebDriverWait(driver, 30)
        time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        search_box = driver.find_element(By.XPATH, '//*[@id="nx_query"]')
        search_box.send_keys(search)
        # Enter 키 전송
        search_box.send_keys(Keys.RETURN)
        qNas = driver.find_elements(By.XPATH, '//*[@id="s_content"]/div[3]/ul/li[*]/dl')

        # 현재 탭의 핸들 가져오기
        original_window = driver.current_window_handle

        for qNa in qNas:
            search_atag = qNa.find_element(By.XPATH, './dt/a')
            question_title = search_atag.text
            question_url = search_atag.get_attribute('href')
            answer_date = qNa.find_element(By.XPATH, './dd[1]').text
            answer_content = qNa.find_element(By.XPATH, './dd[2]').text
            print('질문 : ',question_title, '링크 :', question_url, '답변 일자:', answer_date, '답변 내용:', answer_content)

            # 새 탭에서 질문 클릭
            search_atag.click()
            # 현재 열린 탭들의 핸들 가져오기
            all_windows = driver.window_handles
            # 새로 열린 탭의 핸들 찾기
            new_window = [window for window in all_windows if window != original_window][0]
            # 새로운 탭으로 전환
            driver.switch_to.window(new_window)

            # 질문 내용 가져오기
            question_content = driver.find_element(By.XPATH,'//*[@id="content"]/div[1]/div/div[1]/div[3]').text
            # 질문 작성자 -> 비공개로 떠서 저장 제외
            # question_auth = driver.find_element(By.XPATH,'//*[@id="content"]/div[1]/div/div[3]/div[1]/div/span').text
            # 질문 작성일자
            question_date = driver.find_element(By.XPATH,'//*[@id="content"]/div[1]/div/div[3]/div[1]/span[1]').text
            # 질문 조회수
            question_hit = driver.find_element(By.XPATH,'//*[@id="content"]/div[1]/div/div[3]/div[1]/span[2]').text


            print('질문 내용 :', question_content)
            # print('질문 작성자 : ', question_auth)
            print('질문 작성일자 : ', question_date)
            print('질문 조회수 : ', question_hit)
            # 질문과 답변을 딕셔너리로 묶어서 리스트에 추가
            question_data = {
                'title': question_title,
                'url': question_url,
                'answer_date': answer_date,
                'answer_content': answer_content,
                'question_content': question_content,
                'question_date': question_date,
                'question_hit': question_hit
            }
            result.append(question_data)

            # answer_auth = wait.until(EC.presence_of_element_located(
            #     (By.XPATH, '//*[@id="answer_1"]/div[2]/div[1]/div[1]/div/a/strong'))).text

            # answer_auth = driver.find_element(By.XPATH,'//*[@id="answer_1"]/div[2]/div[1]/div[1]/div/a/strong').text
            # print('답변자', answer_auth)

            # answer_content = driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/div/div[1]/div[2]/div/div[2]/div/div[1]/div[3]/div[1]/div/div/div/div/div/div/p[1]/span').text
            # 답변 내용 가져오기
            # answer_contents = driver.find_elements(By.XPATH,
            #                                        '//div[@class="se-main-container"]/div[@class="se-component-content"]')
            # for index, answer_content in enumerate(answer_contents, start=1):
            #     print(f'답변 {index} 내용:', answer_content.text)

            # 새로운 탭 닫기
            driver.close()
            # 원래 탭으로 전환
            driver.switch_to.window(original_window)

    except (TimeoutException, NoSuchElementException) as e:
        print('지정한 요소를 찾을수 없어요:', e)
    finally:
        pass
        # driver.quit()
    return result