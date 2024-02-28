from flask_restful import Resource
from flask import request, make_response, jsonify
import base64
from PIL import Image
import json
import io
import os
from ultralytics import YOLO
from basic_fuc import db_conn, query_insert, db_disconn, query_select

class foodOcr(Resource):
    def __init__(self):
        self.model = YOLO('best.pt')
    def post(self):
        base64Encoded = request.form['base64Encoded']
        image_b64 = base64.b64decode(base64Encoded)
        image_memory = Image.open(io.BytesIO(image_b64)) #이미지 파일로 디코딩
        image_memory.save('./static/images_foodOcr/new.jpg') #물리적으로 이미지 저장
        results = self.model.predict(['./static/images_foodOcr/new.jpg'],save=True, save_txt= True)

        # pred_image = Image.open(os.path.join(results[0].save_dir, 'new.jpg'))
        # pred_image.show()

        # # 텍스트 파일 열기
        with open(os.path.join(results[0].save_dir, 'labels', 'new.txt'), 'r') as f:
        # with open('./runs/detect/predict/labels/new.txt', 'r') as f:
            # 파일의 각 줄을 리스트에 저장
            lines = f.readlines()

        detected_food_names = []

        # 결과 출력
        for line in lines:
            print('txt 내 라인 출력 )', line.strip())  # 각 줄의 앞뒤 공백 제거 후 출력
            food_index = int(line.split(' ')[0])
            food_names = results[0].names  # 해당 결과의 음식 이름 딕셔너리
            print('음식 인덱스 : ',food_index)
            print('result를 볼까?', results)
            detected_food_names.append(food_names[food_index])

        print('Detected food names:', detected_food_names)

        # print('results\n',results)
        # print('results[0].save_dir\n', results[0].save_dir)
        with open(os.path.join(results[0].save_dir, 'new.jpg'),'rb') as f:
            base64Predicted= base64.b64encode(f.read()).decode('utf-8')
        # print('base64Predicted\n',base64Predicted)

        # 결과를 JSON으로 반환
        response_data = {
            'base64': base64Predicted,
            'detected_food_names': detected_food_names
        }

        return make_response(json.dumps(response_data, ensure_ascii=False))
        # return make_response(json.dumps({'base64': base64Predicted}, ensure_ascii=False))