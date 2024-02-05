from flask import make_response
from flask_restful import Resource, reqparse
import json
from google.cloud import language_v1
from chat_AI import AIChatBot


def textFeelingDetection(text):
    client = language_v1.LanguageServiceClient()  # client 객체 생성
    document = language_v1.types.Document(
        content=text, type_=language_v1.types.Document.Type.PLAIN_TEXT
    )
    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(
        request={"document": document}
    ).document_sentiment
    return {'score':sentiment.score, 'mag':sentiment.magnitude}
class TextEmotionDetection(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('diary', location='args')
        diary = parser.parse_args()['diary'] #사용자가 입력한 일기 내용
        print('구글 api 테스트(요청받은 값): ',diary)
        score = textFeelingDetection(diary)['score'] #긍부정 수치
        mag = textFeelingDetection(diary)['mag'] #감정 복잡도 수치
        messages = [{"role": "assistant", "content": '''
                너는 앞으로 따듯한 말을 건넬 줄 아는 친구의 역할을 해야 해. 너에게는 3개의 정보가 주어질거야.
                1. 사용자가 작성한 일기 내용
                2. 일기의 전반적인 정서에 대한 수치값
                3. 일기에 담긴 감정의 복잡도 
                전반적인 정서에 대한 수치값은 -1부터 1 사이의 값을 가지고 있어. -1에 가까울 수록 부정적인 감정을 의미하고 1에 가까울 수록 긍정적인 감정을 의미하며 0에 가까울수록 중립적인 감정을 의미해. 
                일기에 담긴 감정의 복잡도 에 대한 수치는 값이 0에 가까울수록 감정이 단순한 것을 의미하며 높을수록 사용자가 많은 감정을 가지고 있음을 의미해. 그래서 만약 일기의 전반적인 정서에 대한 수치값이 0인데 일기에 담긴 감정의 복잡도에 대한 수치가 높다면 그건 실제로 사용자가 복잡한 감정을 가지고 있음을 의미하는 거야.
                이러한 정보를 토대로 사용자의 감정에 잘 공감해주는 친구가 되어 적절히 응답해줘. 단, 응답 시에는 100자가 넘지 않아야 하며 존댓말로 대답해야 해. 응답할 때 '안녕하세요'는 빼줬으면 좋겠어.
                '''}]
        content = f'1. 사용자가 작성한 일기 내용: ${diary}\n\n2. 일기의 전반적인 정서에 대한 수치값: ${score}\n\n3. 일기에 담긴 감정의 복잡도: ${mag}'
        response = AIChatBot(content, messages=messages)
        print('받은 응답메세지ㅣ', response)
        messages = response['messages']
        if response['status'] == 'SUCCESS':
            answer = response['messages'][len(messages) - 1]['content']
            print(f'챗봇:{answer}')
            return {'answer':answer, 'score':score}
        else:
            print(messages)
