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


# 유저가 검색하면 크롤링 후 DB에 저장하는 API
class fileNrecipeCrawling(Resource):
    def get(self):
        print('들어왕ㅆ니?')
        file_path = './FOODLIST.csv'
        csv_data = read_csv_file(file_path)
        crawling(csv_data)
        return "크롤링 작업이 성공적으로 실행되었습니다."


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


def crawling(csv_data):
    connection = db_conn()
    # 읽어온 데이터 출력
    for row in csv_data:
        foodname = row[0]
        datatype = row[1]
        category = row[2]
        calory = row[3]
        carbohydrate = row[4]
        protein = row[5]
        fat = row[6]
        sodium = row[7]
        cholesterol = row[8]
        recipecode = row[9]
        url = f'https://www.10000recipe.com/recipe/{recipecode}'
        print(
            f'음식명:{foodname} | 데이터타입 :{datatype} | 카테고리:{category} | 칼로리:{calory} | 탄수화물:{carbohydrate} | 단백질:{protein}| 지방:{fat} | 나트륨:{sodium}| 콜레스테롤:{cholesterol} | url:{url}')

        # 아래는 FOODLIST에 데이터 넣는 코드 (완료)
        # insert_query = "INSERT INTO FOODLIST(foodname, datatype, category, calory,carbohydrate, protein, fat, sodium, cholesterol) VALUES (:foodname, :datatype, :category, :calory, :carbohydrate, :protein, :fat, :sodium, :cholesterol)"
        # query_insert(connection, query=insert_query, foodname=foodname, datatype=datatype,category=category, calory=calory, carbohydrate=carbohydrate, protein=protein, fat=fat, sodium=sodium, cholesterol=cholesterol)

        driver_path = f'{os.path.join(os.path.dirname(__file__), "chromedriver.exe")}'
        # 웹드라이버를 위한 Service객체 생성
        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # headless 모드 설정
        # 자동종료 막기
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=service, options=options)
        # 2.브라우저에 네이버 로그인페이지 로딩하기
        driver.get(url)  # form에 있는 액션 url
        time.sleep(2)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        recipe_title_value = driver.find_element(By.XPATH, '//*[@id="contents_area_full"]/div[3]/h3').text
        print(f'레시피 제목:{recipe_title_value}')
        recipeCode = url.rsplit("/", 1)[-1]
        print(f'레시피 코드:{recipeCode}')

        # 요리명 가져오기 -> 구조 변경으로 요리명 가져올 수가 없어서 제거
        try:
            cooking_orders = []  # 조리 순서를 담을 리스트를 생성합니다.
            step_number = 1  # 초기 스텝 번호
            while True:
                xpath = '//*[@id="stepdescr{}"]'.format(step_number)
                try:
                    Cooking_order = driver.find_element(By.XPATH, xpath)
                    cooking_orders.append(Cooking_order.text.replace('\n', '-'))  # 조리 순서를 리스트에 추가합니다.
                    # 다음 스텝으로 넘어가기 위해 스텝 번호를 증가시킵니다.
                    step_number += 1
                except NoSuchElementException:
                    break

            recipe_seq_str = '|| '.join(cooking_orders)
            print(f'조리 순서 : {recipe_seq_str}')
            recipe_image = driver.find_element(By.XPATH, '//*[@id="main_thumbs"]').get_attribute('src')
            print(f'이미지 링크 : {recipe_image}')

            select_query = "SELECT COUNT(*) FROM Recipe WHERE recipeCode = :recipeCode"
            select_result = query_select(connection, query=select_query, recipeCode=recipeCode)
            print('여기까지 완료?')
            print(select_result)
            if select_result[0][0] == 0:
                print(
                    f'그럼 여기까지는 들어왔나? recipeCode:{recipeCode} | foodname:{foodname}| recipe_url:{url} | recipe_title:{recipe_title_value} | recipe_img:{recipe_image}')
                insert_query = "INSERT INTO Recipe(recipeCode, foodname, recipe_url, recipe_title, recipe_img, recipe_seq) VALUES (:recipeCode, :foodname, :recipe_url, :recipe_title, :recipe_img, :recipe_seq)"
                query_insert(connection, query=insert_query, recipeCode=recipeCode, foodname=foodname, recipe_url=url,
                             recipe_title=recipe_title_value, recipe_img=recipe_image, recipe_seq=recipe_seq_str)
                recipe_info(connection, driver, recipeCode)
            else:
                print("해당 레시피는 DB에 이미 존재하지만 업데이트 합니다.")
                update_query = "UPDATE Recipe SET recipe_seq = :recipe_seq WHERE recipeCode = :recipeCode"
                query_insert(connection, query=update_query, recipeCode=recipeCode, recipe_seq=recipe_seq_str)
                print("업데이트 완료")
                recipe_info(connection, driver, recipeCode)
        except TimeoutException:
            print("시간 내 요소를 못찾았습니다.")
            pass
        except NoSuchElementException:
            print("찾는 요소가 없습니다.")
            pass

    db_disconn(connection)


#####################################################################
# 레시피별 세부 정보 가져오기
def recipe_info(connection, driver, recipeCode):
    print('재료쪽에는 못들어왔어?')
    # 재료 정보 가져오기 (재료, 투입량, 구매 링크) -> 여기서 ul 개수를 체크할 필요가 있을 것 같음. (ul이 하나면 재료만 적힌 것. ul이 두개면 양념이나 다른 추가 정보도 존재..)
    jaros_ultag = driver.find_elements(By.XPATH, '//*[@id="divConfirmedMaterialArea"]/ul[*]')

    print(f'jaros_ultag : {jaros_ultag}')
    for jaro in jaros_ultag:
        jaros_litag = jaro.find_elements(By.XPATH, './li[*]')
        print(f'li - {jaros_litag}')
        for li in jaros_litag:
            ingredient = li.find_element(By.XPATH, './a[1]').text
            print(f'재료명 :{ingredient}')
            jaro_span = li.find_element(By.XPATH, './span').text
            print(f'투입량 : {jaro_span}')

            select_query = "SELECT COUNT(*) FROM Recipe_ingredients WHERE ingredient = :ingredient and recipeCode = :recipeCode"
            select_result = query_select(connection, query=select_query, ingredient=ingredient, recipeCode=recipeCode)
            if select_result[0][0] == 0:
                insert_query = "INSERT INTO Recipe_ingredients(ingredient, recipeCode, RI_amount) VALUES (:ingredient, :recipeCode, :RI_amount)"
                query_insert(connection, query=insert_query, ingredient=ingredient, recipeCode=recipeCode,
                             RI_amount=jaro_span)
                print('재료 업로드 성공')
            else:
                print("해당 재료가 이미 DB에 존재..")