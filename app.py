from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from create_image import CreateImage
from crawling import areaCrawling

#플라스크 앱 생성
app = Flask(__name__)
#CORS에러 처리
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

api.add_resource(CreateImage, '/CreateIm')
api.add_resource(areaCrawling, '/areaCrawling')
api.decorators=[CORS()]

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)