from konlpy.tag import Okt
import os

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from flask_restful import Resource
from selenium.webdriver.common.keys import Keys
from basic_fuc import db_conn, query_insert, db_disconn, query_select

########################## 사이트에서 레시피 설명 가져오고 형용사를 추출해보기... ########################################
# def crawl_recipe(urllink):
#     driver = webdriver.Chrome(service=service, options=options)
#     # 2.브라우저에 네이버 로그인페이지 로딩하기
#     driver.get(urllink)  # form에 있는 액션 url
#     time.sleep(2)  # 페이지가 완전히 로딩되도록 3초동안 기다림
#     recipe_sentence = driver.find_element(By.XPATH,'//*[@id="recipeIntro"]').text
#     print('추출 문장 :', recipe_sentence)
#     okt = Okt()
#     pos_tags = okt.pos(recipe_sentence)
#
#     # 추출된 형용사와 부사 중에서 필요한 부분만 추출
#     adjectives = [word for word, pos in pos_tags if pos == 'Adjective']
#
#     # 웹 드라이버 종료
#     driver.quit()
#
#     return adjectives
#
# # 1.WebDriver객체 생성
# driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
# # 웹드라이버를 위한 Service객체 생성
# service = Service(executable_path=driver_path)
# options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # headless 모드 설정
# # 자동종료 막기
# options.add_experimental_option("detach", True)
#
# connection = db_conn()
# select_query = "SELECT RECIPECODE,RECIPE_URL FROM Recipe"
# select_result = query_select(connection, query=select_query)
#
# for recipecode, recipe_url in select_result:
#     adjectives = crawl_recipe(recipe_url)
#     print(f"레시피 코드: {recipecode}, 레시피 특징: {adjectives}")

########################################################################################################