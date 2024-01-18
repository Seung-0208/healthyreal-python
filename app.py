from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from api.create_image import CreateImage

#플라스크 앱 생성
app = Flask(__name__)
#CORS에러 처리
CORS(app)

api = Api(app)

api.add_resource(CreateImage, '/CreateIm')

if __name__ == '__main__':
    app.run(debug=True)
