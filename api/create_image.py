import os
import urllib.request
from openai import OpenAI
from flask import jsonify
from flask_restful import Resource
from flask import request

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class CreateImage(Resource):
    def post(self):
        prompt = request.json['message']  # 뷰에서 넘긴 메세지 받기
        print('받은 메세지:', prompt)
        image_path, image_name = generate_image(prompt, client)
        image_url = '/' + image_path.replace('\\', '/')
        print('보내는 메세지:', image_url)
        print('보내는 메세지:', image_name)
        return jsonify({"image_url": image_url, "image_name": image_name})

# 폴더 생성 함수
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def create_image(client, model, messages):
    response = client.chat.completions.create(model=model, messages=messages)
    return response

def generate_image(prompt, client):
    model = 'gpt-3.5-turbo'

    print('받은 메세지2:', prompt)
    messages = [
        {"role": "system", "content": "you are a translation expert who translates korean into english"},
        {"role": "user", "content": prompt}
    ]
    print('반환 메세지:', messages)

    response = create_image(client, model, messages)
    prompt = response.choices[0].message.content
    print('번역:', prompt)
    folder_path = 'static/upload_image'  # 'static' 폴더 아래에 이미지 저장
    create_folder_if_not_exists(folder_path)

    image_name = 'Id.jpg'
    image_path = os.path.join(folder_path, image_name)

    if os.path.exists(image_path):
        # 중복된 이미지 이름이 있을 경우, 숫자를 추가하여 중복 피하기
        index = 1
        while os.path.exists(image_path):
            image_name = f'Id_{index}.jpg'
            image_path = os.path.join(folder_path, image_name)
            index += 1
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format='url',
        n=1,
    )

    image_url = response.data[0].url  # 1시간만 유효
    print('이미지 경로:', image_url)
    urllib.request.urlretrieve(image_url, image_path)

    return image_path, image_name

