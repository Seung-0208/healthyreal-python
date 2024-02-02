import os

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from flask import request
from flask_restful import Resource
from selenium.webdriver.common.keys import Keys
from basic_fuc import db_conn, query_insert, db_disconn, query_select

#유저가 검색하면 크롤링 후 DB에 저장하는 API
class recipeCrawlingAPI(Resource):
    def get(self):
        urllink = 'https://www.10000recipe.com/recipe/list.html'
        basic_setting(urllink)
        return "크롤링 작업이 성공적으로 실행되었습니다."

#크롤링할 url 설정 함수
def basic_setting(urllink):
    # 1.WebDriver객체 생성
    driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
    # 웹드라이버를 위한 Service객체 생성
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # headless 모드 설정
    # 자동종료 막기
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service, options=options)
    # 2.브라우저에 네이버 로그인페이지 로딩하기
    driver.get(urllink)  # form에 있는 액션 url
    time.sleep(2)  # 페이지가 완전히 로딩되도록 3초동안 기다림

    # 분류 - 상황별 - 일상
    driver.find_element(By.XPATH, '//*[@id="id_search_category"]/table/tbody/tr[1]/td/div/div[2]/a[8]').click()
    time.sleep(1)

    # 레시피 제목 가져오기
    recipes = driver.find_elements(By.XPATH, '//*[@id="contents_area_full"]/ul/ul/li[*]')
    # div[1] > a > span과 img (span 태그가 있으면 동영상 존재)
    # div[2] > div[1]에는 타이틀 / div[2]에는 유저정보 / div[3]에는 조회수 & 별점
    get_recipe(driver, recipes)

#레시피 정보 가져오기
def get_recipe(driver, recipes):
    connection = db_conn()
    ind = 1

    for recipe in recipes:
        print(f'[{ind}]')
        time.sleep(3)
        div_tags = recipe.find_elements(By.XPATH, './div')

        # 링크,img + span유무에 따른 동영상 여부
        first_div = div_tags[0]
        first_in_a = first_div.find_element(By.TAG_NAME, 'a')
        # 레시피 링크
        href_value = first_in_a.get_attribute('href')

        # 제목,유저정보,조회수&별점
        second_div = div_tags[1]
        second_in_div = second_div.find_elements(By.XPATH, './div')
        recipe_title = second_in_div[0] #제목

        print(f'제목:{recipe_title.text}, 링크:{href_value}')
        recipeCode = href_value.rsplit("/", 1)[-1]
        print('레시피 코드:',recipeCode)

        # 이전 탭에서 가져온 recipe_title 값을 저장
        recipe_title_value = recipe_title.text
        # 현재 탭의 핸들 저장
        current_tab = driver.current_window_handle
        # 요리 상세보기 링크를 새로운 탭에서 열기
        first_in_a.send_keys(Keys.CONTROL + Keys.RETURN)
        # 새로 열린 탭으로 전환
        driver.switch_to.window(driver.window_handles[-1])
        wait = WebDriverWait(driver, 30)
        # URL에 recipeCode 값을 포함시켜 전달
        driver.get(f"{driver.current_url}?recipeCode={recipeCode}")

        # URL에서 recipeCode 값을 읽어옴
        url = driver.current_url
        recipeCode = url.split('=')[-1]
        time.sleep(3)

        # 요리명 가져오기
        try:
            food_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="relationGoods"]/div[1]/b[1]')))
            print(f'요리명:{food_name.text}')
            select_query = "SELECT COUNT(*) FROM Foodlist WHERE foodname = :food_name"
            select_result = query_select(connection, query=select_query, food_name=food_name.text)
            if select_result[0][0] == 0:
                insert_query = "INSERT INTO Foodlist(foodname, dataType) VALUES (:food_name, 1)"
                query_insert(connection, query=insert_query, food_name=food_name.text)
            else:
                print("해당 음식은 DB에 이미 존재")

            select_query = "SELECT COUNT(*) FROM Recipe WHERE recipeCode = :recipeCode"
            select_result = query_select(connection, query=select_query, recipeCode=recipeCode)
            if select_result[0][0] == 0:
                recipe_url = f"https://www.10000recipe.com/recipe/{recipeCode}"
                insert_query = "INSERT INTO Recipe(recipeCode, foodname, recipe_url, recipe_title) VALUES (:recipeCode, :food_name, :recipe_url, :recipe_title)"
                query_insert(connection, query=insert_query, recipeCode=recipeCode, food_name=food_name.text,
                             recipe_url=recipe_url, recipe_title=recipe_title_value)
            else:
                print("해당 레시피는 DB에 이미 존재")
        except TimeoutException:
            print("시간 내 요소를 못찾았습니다.")
            pass
        except NoSuchElementException:
            print("찾는 요소가 없습니다.")
            pass

        recipe_info(connection, driver, wait, current_tab, recipeCode)
        ind += 1
    db_disconn(connection)

#####################################################################
#레시피별 세부 정보 가져오기
def recipe_info(connection,driver, wait, current_tab, recipeCode):
    # 재료 정보 가져오기 (재료, 투입량, 구매 링크) -> 여기서 ul 개수를 체크할 필요가 있을 것 같음. (ul이 하나면 재료만 적힌 것. ul이 두개면 양념이나 다른 추가 정보도 존재..)
    jaros = driver.find_elements(By.XPATH, '//*[@id="divConfirmedMaterialArea"]/ul[1]/li[*]')
    for jaro in jaros:
        a_tags = jaro.find_elements(By.XPATH, './a')
        first_a_tag = a_tags[0]  # 첫 번째 a 태그  -- 재료의 info 링크
        second_a_tag = a_tags[1]  # 두 번째 a 태그 -- 구매와 관련된 링크
        span_tag = jaro.find_element(By.XPATH, './span')
        print(f'재료 : {first_a_tag.text}  - 투입량 : {span_tag.text} - 구매 링크 : {second_a_tag.get_attribute("href")}')

        select_query = "SELECT COUNT(*) FROM Recipe_ingredients WHERE ingredient = :ingredient and recipeCode = :recipeCode"
        select_result = query_select(connection, query=select_query, ingredient=first_a_tag.text, recipeCode=recipeCode)
        if select_result[0][0] == 0:
            insert_query = "INSERT INTO Recipe_ingredients(ingredient, recipeCode, RI_amount) VALUES (:ingredient, :recipeCode, :RI_amount)"
            query_insert(connection, query=insert_query, ingredient=first_a_tag.text, recipeCode=recipeCode,
                      RI_amount=span_tag.text)
        else:
            print("해당 재료가 이미 DB에 존재..")

        # #각종 광고 제거
        # delete_abs(driver,wait)
        # #재료별 상세 정보
        # ingredient_info(driver, wait, first_a_tag)

    # 새로운 탭 닫기
    driver.close()
    # 기존 탭으로 전환
    driver.switch_to.window(current_tab)



#재료의 상세정보
def ingredient_info(driver, wait, first_a_tag):
    first_a_tag.click()
    time.sleep(3)  # 모달 클릭 이후 정보를 동적정보를 가지고 오는동안 대기

    try:
        print('들어옴')
        # 재료 상세정보
        jaroinfos = driver.find_elements(By.XPATH, '//*[@id="materialBody"]/div/div[2]/table/tbody/tr[*]')
        print(jaroinfos)
        for jaroinfo in jaroinfos:
            jaroinfo_th = jaroinfo.find_element(By.XPATH, './th')
            jaroinfo_td = jaroinfo.find_element(By.XPATH, './td')
            print(f'{jaroinfo_th.text} - {jaroinfo_td.text}')
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="materialViewModal"]/div/div/div[1]/button/img'))).click()
        print('닫기 버튼 클릭')
    except NoSuchElementException:
        # tbody나 tr 요소가 존재하지 않는 경우에 대한 예외 처리
        print("해당 항목이 없습니다.")
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="materialViewModal"]/div/div/div[1]/button/img'))).click()
        pass


#####################################################################
#광고 제거 함수
def delete_abs(driver,wait):
    # 구글 광고로 클릭이 안되는 이슈 해결
    # try:
    #     driver.find_element(By.XPATH, '/html/body/div[5]/div/div/div[2]').click()
    #     print('구글광고 닫기 완료')
    # except NoSuchElementException:
    #     pass

    # 광고 모달 닫기
    try:
        time.sleep(3)
        # ad_modal = driver.find_element(By.XPATH, '//*[@id="popup_goods"]/a')
        ad_modal = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="popup_goods"]/a')))
        print('레시피광고 찾기 완료')
        time.sleep(5)
        ad_modal.click()
        print('레시피모달 닫기 완료')
    except NoSuchElementException:
        pass


# 스크롤 값을 받아 특정 위치로 스크롤을 내리는 함수
def scroll_to_position(driver, scroll_value):
    script = "window.scrollTo(0, {});".format(scroll_value)
    driver.execute_script(script)
