import requests
import json
from flask import request
from flask_restful import Resource

APIKEY = "56ce4888feecb9827e0e78ecdff1f09b"
LANG = "kr"
class weather_info(Resource):
    def post(self):
        location = request.json['location']
        print(location)
        city = areainfo(location)
        weatherData = getweather(city)
        return weatherData
    def get(self):
        location = request.args.get('location')
        print(location)
        city = areainfo(location)
        weatherData = getweather(city)
        return weatherData

def getweather(city):
    api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={APIKEY}&lang={LANG}&units=metric"
    result = requests.get(api)
    data = json.loads(result.text)
    # # 지역 : name
    print(data)
    print(data["name"],"의 날씨입니다.")
    # 자세한 날씨 : weather - description
    print("날씨는 ",data["weather"][0]["description"],"입니다.")
    # 현재 온도 : main - temp
    print("현재 온도는 ",data["main"]["temp"],"입니다.")
    # 체감 온도 : main - feels_like
    print("하지만 체감 온도는 ",data["main"]["feels_like"],"입니다.")
    # 최저 기온 : main - temp_min
    print("최저 기온은 ",data["main"]["temp_min"],"입니다.")
    # 최고 기온 : main - temp_max
    print("최고 기온은 ",data["main"]["temp_max"],"입니다.")
    # 습도 : main - humidity
    print("습도는 ",data["main"]["humidity"],"입니다.")
    # 기압 : main - pressure
    print("기압은 ",data["main"]["pressure"],"입니다.")
    # 풍향 : wind - deg
    print("풍향은 ",data["wind"]["deg"],"입니다.")
    # 풍속 : wind - speed
    print("풍속은 ",data["wind"]["speed"],"입니다.")
    return data

def areainfo(city):
#수도권
    if(city == '서울') : return 'Seoul'
    elif(city == '구리'): return 'Guri-si'
    elif (city == '하남'):return 'Hanam'
    elif (city == '김포'):return 'Gimpo-si'
    elif (city == '화도'):return 'Hwado'
    elif (city == '문산'):return 'Munsan'
    elif (city == '파주'):return 'Paju'
    elif (city == '고양'):return 'Goyang-si'
    elif (city == '의정부'):return 'Uijeongbu-si'
    elif (city == '가평'):return 'Gapyeong County'
    elif (city == '양평'):return 'Yangpyong'
    elif (city == '수원'):return 'Suwon-si'
    elif (city == '오산'):return 'Osan'
    elif (city == '용인'):return 'Yongin'
    elif (city == '이천'): return 'Icheon-si'
    elif (city == '여주'):return 'Yeoju'
    elif (city == '평택'):return 'Pyeongtaek-si'
#인천
    elif (city == '인천'):return 'Incheon'
    elif (city == '강화'):return 'Ganghwa-gun'
    elif (city == '부천'):return 'Bucheon-si'
#강원권
    elif (city == '춘천'):return 'Chuncheon'
    elif (city == '원주'):return 'Wonju'
    elif (city == '제천'):return 'Jecheon'
    elif (city == '태백'):return 'Taebaek'
    elif (city == '울진'):return 'Ulchin'

#충북
    elif (city == '충주'):return 'Chungju'
    elif (city == '괴산'):return 'Koesan'
    elif (city == '영주'):return 'Yeongju'
    elif (city == '진천'):return 'Chinchon'
    elif (city == '청주'):return 'Cheongju-si'
    elif (city == '옥천'):return 'Okcheon'
    elif (city == '영동'):return 'Yeongdong'

#충남
    elif (city == '아산'):return 'Asan'
    elif (city == '서산'):return 'Seosan CIty'
    elif (city == '예산'):return 'Yesan'
    elif (city == '홍성'):return 'Hongseong'
    elif (city == '천안'):return 'Cheonan'
    elif (city == '공주'):return 'Gongju'
    elif (city == '논산'):return 'Nonsan'
    elif (city == '부여'):return 'Buyeo'

#전라북도
    elif (city == '안양'):return 'Anyang-si'
    elif (city == '안산'):return 'Ansan-si'
    elif (city == '성남'):return 'Seongnam-si'
    elif (city == '괴내'): return 'Goenae'
    elif (city == '연천'):return 'Yeoncheon-gun'

    elif (city == '대전'):return 'Daejeon'
    elif (city == '장골'):return 'Janggol'
    elif (city == '무주'):return 'Muju'
    elif (city == '군산'):return 'Gunsan'
    elif (city == '익산'):return 'Iksan'
    elif (city == '전주'):return 'Jeonju'
    elif (city == '김제'):return 'Kimje'
    elif (city == '푸안'):return 'Puan'
    elif (city == '진안'):return 'Jinan-gun'
    elif (city == '임실'):return 'Imsil'
    elif (city == '고령'):return 'Koryong'
    elif (city == '함양'):return 'Hamyang'
    elif (city == '창수'):return 'Changsu'
    elif (city == '영광'):return 'Yeonggwang'
    elif (city == '나주'):return 'Naju'
    elif (city == '무안'):return 'Muan'
    elif (city == '함평'):return 'Hampyeongsaengtaegongwon'
    elif (city == '광주'):return 'Gwangju'
    elif (city == '신안'):return 'Sinan'
    elif (city == '목포'):return 'Mokpo'
    elif (city == '영암'):return 'Yeongam-guncheong'
    elif (city == '보성'):return 'Boseong'
    elif (city == '벌교'):return 'Beolgyo'
    elif (city == '해남'):return 'Haenam'
    elif (city == '순천'):return 'Suncheon'
    elif (city == '산곡'):return 'Sangok'
    elif (city == '남해'):return 'Namhae'
    elif (city == '하동'):return 'Hadong-eup Samuso'
    elif (city == '고성'):return 'Goseong'
    elif (city == '진주'):return 'Jinju'
    elif (city == '구례'):return 'Kurye'
    elif (city == '부산'):return 'Busan'
    elif (city == '기장'):return 'Gijang'
    elif (city == '진해'):return 'Chinhae'
    elif (city == '마산'):return 'Masan'
    elif (city == '창원'):return 'Changwon'
    elif (city == '김해'):return 'Gimhae'
    elif (city == '밀양'):return 'Miryang'
    elif (city == '울산'):return 'Ulsan'
    elif (city == '창녕'):return 'Changnyeong'
    elif (city == '경산'): return 'Gyeongsan-si'
    elif (city == '대구'):return 'Daegu'
    elif (city == '칠곡'):return 'Chilgok'
    elif (city == '경주'):return 'Gyeongju'
    elif (city == '포항'):return 'Pohang'
    elif (city == '구미'):return 'Gumi'
    elif (city == '초곡'):return 'Chogok'
    elif (city == '김천'):return 'Cimcheon'
    elif (city == '안동'):return 'Andong'
    elif (city == '예천'):return 'Yecheon'
    elif (city == '문경'):return 'Mungyeong'
    elif (city == '청송'):return 'Cheongsong gun'
    elif (city == '제주'):return 'Jeju City'
    elif (city == '홍천'):return 'Hongchon'
    elif (city == '협평'):return 'Hupyong'
    elif (city == '동해'):return 'Tonghae'
    elif (city == '강릉'):return 'Gangneung'
    elif (city == '양양'):return 'Yangyang'
    elif (city == '인제'):return 'Inje'
    elif (city == '양구'):return 'Yanggu'
    elif (city == '화천'):return 'Hwacheon'
    elif (city == '연천'):return 'Yeoncheon-gun'
    elif (city == '황매'):return 'Hwangmae'
    else:return 'Seoul'




# city = "Seoul"
# apikey = "56ce4888feecb9827e0e78ecdff1f09b"
# lang = "kr"
# api = f"""http://api.openweathermap.org/data/2.5/\
# weather?q={city}&appid={apikey}&lang={lang}&units=metric"""
#
# result = requests.get(api)
#
# data = json.loads(result.text)
