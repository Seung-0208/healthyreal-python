import os
import urllib.request
from openai import OpenAI
from flask import jsonify
from flask_restful import Resource
from flask import request
import boto3
from botocore.exceptions import NoCredentialsError

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# S3 클라이언트 생성
s3 = boto3.client('s3',
                  aws_access_key_id='',
                  aws_secret_access_key='',
                  region_name='ap-northeast-2')

def upload_to_s3(local_file, bucket, s3_file):
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

class CreateImage(Resource):
    def post(self):
        prompt = request.json['message']  # 뷰에서 넘긴 메세지 받기
        id = request.json['id']  # 뷰에서 넘긴 메세지 받기
        image_path, image_name = generate_image(prompt, client, id)
        return jsonify({"image_url": image_path, "image_name": image_name})

# 폴더 생성 함수
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def create_image(client, model, messages):
    response = client.chat.completions.create(model=model, messages=messages)
    return response

def generate_image(prompt, client, id):
    model = 'gpt-3.5-turbo'
    messages = [
        {"role": "system", "content": "you are a translation expert who translates korean into english"},
        {"role": "user", "content": prompt}
    ]

    response = create_image(client, model, messages)
    prompt = response.choices[0].message.content
    folder_path = 'static/upload_image'
    create_folder_if_not_exists(folder_path)

    image_name = id
    image_path = os.path.join(folder_path, image_name)

    if os.path.exists(image_path):
        index = 1
        while os.path.exists(image_path):
            image_name = f'{id}_{index}.jpg'
            image_path = os.path.join(folder_path, image_name)
            index += 1
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        response_format='url',
        n=1,
    )

    image_url = response.data[0].url
    urllib.request.urlretrieve(image_url, image_path)

    # S3 버킷의 'image' 폴더에 업로드
    s3_file = f"image/{image_name}"
    uploaded = upload_to_s3(image_path, 'ictimg', s3_file)

    if uploaded:
        # S3에 업로드된 파일의 URL을 가져옵니다.
        s3_url = f"https://ictimg.s3.ap-northeast-2.amazonaws.com/{s3_file}"
        return s3_url, image_name
    else:
        return None, None

