from wordcloud import WordCloud
from konlpy.tag import Twitter
from collections import Counter
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib import rc
from flask_restful import Resource
from flask import request, send_file, jsonify
import base64
import io
from PIL import Image
import numpy as np

class wordcloudtest(Resource):
    def post(self):
        # id = request.json['id']
        text = request.json['text']
        img_data = wordcloud_basic(text)
        return jsonify({"image": img_data})
    def get(self):
        # id = request.json['id']
        text = request.args.get('text')
        img_data = wordcloud_basic(text)
        return jsonify({"image": img_data})

def wordcloud_basic(text):
    # 기본 글꼴을 NanumGothic으로 변경
    rc('font', family='NanumGothic')

    # 사용자가 직접 입력한 문장을 변수에 저장
    text = text

    twitter = Twitter()

    # 문장의 형태소를 분석하여 명사와 형용사만 추출하여 리스트에 저장
    sentences_tag = twitter.pos(text)
    noun_adj_list = [word for word, tag in sentences_tag if tag in ['Noun', 'Adjective']]

    # 가장 많이 나온 단어부터 40개를 저장
    counts = Counter(noun_adj_list)
    tags = counts.most_common(40)

    # 시스템에 설치된 한글 폰트 경로를 지정
    font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트의 예시

    # 하트 모양 이미지를 로드하여 마스크로 사용
    mask = np.array(Image.open("./api/heart0.png"))

    # WordCloud 생성 시 폰트 경로 지정
    wc = WordCloud(font_path=font_path, background_color="white", max_font_size=60, mask=mask)

    cloud = wc.generate_from_frequencies(dict(tags))

    # 생성된 WordCloud 이미지를 바이트 스트림으로 저장
    img_data = save_image(cloud)
    print(img_data)
    return img_data

def save_image(cloud):
    # 이미지를 바이트 스트림으로 변환하여 반환
    img_stream = io.BytesIO()
    cloud.to_image().save(img_stream, format='PNG')
    img_stream.seek(0)
    img_data = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    return img_data
