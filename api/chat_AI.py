import os
from openai import OpenAI
from flask import jsonify
from flask_restful import Resource
from flask import request
import openai

#환경 변수에서 OpenAI API 키를 가져옴
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

class ChatAI(Resource):
    def post(self):
        messages = [{"role":"assistant", "content":'''
        You are Helthy-Real's customer service referral bot.
        What we offer is a service PlayStation that provides personal digital maintenance services.
        It can cut into your personal health and recommend only healthy exercises as well as recipes and assets.
        We try to obtain health information in a way that is neutral to the individual.
        When responding, be courteous and polite to all users.
        If you have any questions that do not provide a clear answer, please reply 'Please contact the administrator.'
        Please reply using access since you are a Korean bot and most of your users are the newest
        If the user wishes to cancel payment or reservation, they will be contacted by a counselor at 010-1234-1234.
        Please indicate the link https://health.kdca.go.kr/healthinfo/ for additional health information.
        All answers must be provided in Korean.
        '''}]
        while True:
            content = request.json['message']
            response = AIChatBot(content, messages=messages)
            messages = response['messages']
            if response['status'] == 'SUCCESS':
                answer = response['messages'][len(messages) - 1]['content']
                return jsonify({"answer": answer})
            else:
                print(messages)

def AIChatBot(content,model='gpt-4-turbo-preview',messages=[],temperature=1):
    error=None
    try:
        # 사용자의 메시지를 리스트에 추가
        messages.append({'role':'user','content':content})
        # 메시지를 OpenAI API를 통해 챗봇에게 전달
        response = client.chat.completions.create(model=model, messages=messages)
        # 챗봇의 응답을 리스트에 추가
        answer = response.choices[0].message.content
        messages.append({'role': 'assistant', 'content': answer})
        # 응답 결과를 반환
        return {'status':'SUCCESS','messages':messages}

    # 여러 가지 예외 상황을 처리
    except openai.error.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        error=e
    except openai.error.APIConnectionError as e:
        # Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")
        error = e
    except openai.error.InvalidRequestError as e:
        print(f"Invalid Request to OpenAI API: {e}")
        error = e
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        error = e
    # 실패 시 에러 메시지를 반환
    return {'status': 'FAIL', 'messages': error}


