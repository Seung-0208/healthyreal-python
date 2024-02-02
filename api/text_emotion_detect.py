from flask import make_response
from flask_restful import Resource, reqparse
import json
from google.cloud import language_v1


def textFeelingDetection(text):
    client = language_v1.LanguageServiceClient()  # client 객체 생성
    document = language_v1.types.Document(
        content=text, type_=language_v1.types.Document.Type.PLAIN_TEXT
    )
    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(
        request={"document": document}
    ).document_sentiment

    print(f"결과: {sentiment.score}, {sentiment.magnitude}")
class TextEmotionDetection(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('diary', location='args')
        diary = parser.parse_args()['diary']
        print('구글 api 테스트(요청받은 값): ',diary)
        result = textFeelingDetection(diary)
        return make_response(result)
