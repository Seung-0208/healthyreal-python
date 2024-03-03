from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from create_image import CreateImage
from area_crawling import areaCrawling
from chat_AI import ChatAI
from face_emotion import FaceEmotion
from recipeCrawling_Api import recipeCrawlingAPI
from text_emotion_detect import TextEmotionDetection
from Weather_Info import weather_info
from food_ocr import foodOcr
from OCR import inOcr
from recipeCrawling_csv import fileNrecipeCrawling
from Food_recommendation import food_recommend
from kin_crawling import kinCrawling
from wordcloud3d import wordcloudtest
from youtude_crawling import youtudeCrawling
from Exercise_recommendation import recommendExercise
from wrtnai_crawling import wrtnCrawling
from exercise_crawling import exerciseCrawling
from recommendMate import recommendMate


#플라스크 앱 생성
app = Flask(__name__)
#CORS에러 처리
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

api.add_resource(CreateImage, '/CreateIm')
api.add_resource(areaCrawling, '/areaCrawling')
api.add_resource(ChatAI, '/ChatAI')
api.add_resource(recipeCrawlingAPI, '/recipeCrawlingAPI')
api.add_resource(TextEmotionDetection, '/diary')
api.add_resource(weather_info, '/weatherInfo')
api.add_resource(foodOcr, '/foodOcr')
api.add_resource(inOcr, '/ocr')

api.add_resource(fileNrecipeCrawling, '/fileNrecipeCrawling')
api.add_resource(FaceEmotion, '/test')
api.add_resource(food_recommend, '/food_recommend')
api.add_resource(kinCrawling, '/kinCrawling')
api.add_resource(wordcloudtest, '/wordcloud')
api.add_resource(youtudeCrawling, '/youtudeCrawling')
api.add_resource(recommendExercise, '/recommendExercise')
api.add_resource(wrtnCrawling, '/wrtnCrawling')
api.add_resource(exerciseCrawling, '/exerciseCrawling')
api.add_resource(recommendMate, '/recommendMate')
api.decorators=[CORS()]

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)