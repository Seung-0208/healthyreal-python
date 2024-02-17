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
import json

class areaCrawling(Resource):
    def post(self):
        matearea = request.json['matearea']
        matemonth = request.json['matemonth']
        matedate = request.json['matedate']
        print(matearea, matemonth, matedate)
        return driver_crawling(matearea, matemonth, matedate)

# 사용자가 입력한 지역에 따라 해당 지역번호 반환하는 함수
def area_No(userarea):
    if (userarea == '서울'):return 2
    elif (userarea == '부산'):return 3
    elif (userarea == '인천'):return 4
    elif (userarea == '대전'):return 5
    elif (userarea == '광주'):return 6
    elif (userarea == '대구'):return 7
    elif (userarea == '울산'):return 8
    elif (userarea == '세종'):return 9
    elif (userarea == '경기'):return 10
    elif (userarea == '충북'):return 11
    elif (userarea == '충남'):return 12
    elif (userarea == '전북'):return 13
    elif (userarea == '전남'):return 14
    elif (userarea == '경북'):return 15
    elif (userarea == '경남'):return 16
    elif (userarea == '강원'):return 17
    elif (userarea == '제주'):return 18
    else:return 1

def print_page_data(driver, total_pages, total):
    data_map = {}
    for page in range(1, total_pages+1):
        if page != 1:
            # 다음 페이지로 넘어가는 동작
            driver.find_element(By.ID, f'page-link{page}').click()
            time.sleep(1)  # 페이지 로딩을 기다리기 위한 시간 설정

        titles = driver.find_elements(By.CLASS_NAME, 'ti_txt')
        pays = driver.find_elements(By.CLASS_NAME, 'etc')
        links = driver.find_elements(By.XPATH, '//*[@id="searchList"]/div[1]/ul/li[*]/div')
        imgs = driver.find_elements(By.XPATH,'//*[@id="searchList"]/div[1]/ul/li[*]/div/div/div[1]/img')
        for i in range(20):
            index = (page - 1) * 20 + i
            if index == int(total):
                break
            title = titles[i]
            pay = (pays[i].find_element(By.XPATH, "./*[3]").text).replace("이용 요금", "").replace("\n", "")
            link = links[i].get_attribute('data-linkurl')
            rsrc_no = links[i].get_attribute('data-rsrcno')
            src =  imgs[i].get_attribute("src")
            print(f'이미지 : {src}')
            if link == '/UserPortal/Upv/UprResrcGym/index.do':
                data = {
                    'index': index + 1,
                    'title': title.text,
                    'pay': pay,
                    'link': f'https://www.eshare.go.kr{link}?rsrc_no={rsrc_no}',
                    'src':src
                }
                print(f'{index+1}. 장소명:{title.text} 금액:{pay} 링크:https://www.eshare.go.kr{link}?rsrc_no={rsrc_no} 이미지:{src}')
            else:
                data = {
                    'index': index + 1,
                    'title': title.text,
                    'pay': pay,
                    'link': link,
                    'src': src
                }
                print(f'{index + 1}. 장소명:{title.text} 금액:{pay} 링크:{link} 이미지:{src}')
            data_map[index + 1] = data
    return data_map


def driver_crawling(matearea, matemonth, matedate):
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
        # 2.브라우저에 네이버 로그인페이지 로딩하기
        driver.get('https://www.eshare.go.kr/UserPortal/adv/resources/AdvEsSearchResourcesMainView.do?rsrcClsCd=010500')  # form에 있는 액션 url
        time.sleep(3)  # 페이지가 완전히 로딩되도록 3초동안 기다림

        # 검색어 입력
        # search_box = driver.find_element(By.XPATH, '//*[@id="searchRsrcNm"]')
        # search_box.send_keys('')  # 검색어가 있으면 활용
        # 희망지역 (시도)
        driver.find_element(By.NAME, 'sido').click()
        time.sleep(1)
        areano = area_No(matearea)  # 메이트 방 지역 설정에 따른 시도값 받기
        driver.find_element(By.XPATH, f'//*[@id="dtlSido"]/option[{areano}]').click()
        time.sleep(1)
        # 예약 구분 값 선택 (실시간예약 - 홈페이지 내)
        driver.find_element(By.ID, 'searchIntnetRsrvPsblYn_Y').click()
        time.sleep(1)

        # 날짜 선택
        driver.find_element(By.XPATH, f'//*[@id="searchDate"]').click()
        wait = WebDriverWait(driver, 5)

        # 날짜 선택을 위해 달력이 나타날 때까지 대기
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'xdsoft_calendar')))

        # 월 선택
        # 월 리스트 버튼 클릭
        driver.find_element(By.XPATH, '/html/body/div[6]/div[1]/div[1]/div[1]').click()
        time.sleep(1)
        action = ActionChains(driver)
        time.sleep(5)
        monthList = driver.find_elements(By.CLASS_NAME, 'xdsoft_option')
        # time.sleep(2)
        action.move_to_element(monthList[matemonth - 1]).perform()
        monthList[matemonth - 1].click()
        time.sleep(2)

        # 일자 선택
        element_container = driver.find_element(By.XPATH,
                                                "/html/body/div[6]/div[1]/div[2]/table/tbody")  # 요소를 포함하는 컨테이너 요소의 XPath 경로를 지정합니다.
        elements = element_container.find_elements(By.XPATH, f".//*[contains(text(), '{matedate}')]")
        element_container.find_element(By.XPATH, f".//*[text()='{matedate}']").click()  # 컨테이너 요소 내에서만 클릭 동작을 수행합니다.
        time.sleep(1)

        # 검색
        driver.find_element(By.XPATH, '//*[@id="UprResrcSearchForm"]/article/div/div[2]/a').click()

        # 페이지가 완전히 로딩되도록 3초동안 기다림
        time.sleep(3)

        # 나온 항목들의 title값 가져오기
        total = driver.find_element(By.XPATH, '//*[@id="searchList"]/p/span/em').text
        total_pages = int(total) // 20 + 1
        if int(total) % 20 == 0:
            total_pages -= 1

        crawling_json = print_page_data(driver, total_pages=total_pages, total=total)
        print(crawling_json)
        return crawling_json
    except (TimeoutException, NoSuchElementException) as e:
        print('지정한 요소를 찾을수 없어요:', e)
    finally:
        driver.quit()