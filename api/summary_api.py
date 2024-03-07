from flask_restful import Resource, reqparse
import requests
import json

class summaryAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('content', type = list, required = True,
                                   help = 'No content provided', location = 'json')

        self.client_id = "jt77dperz3"
        self.client_secret = "uRiFIhLE3e9dPH0PM3T9Qep6UbL7F3QuqwOXjZxU"
        self.url = 'https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize'

        self.headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-NCP-APIGW-API-KEY-ID': self.client_id,
            'X-NCP-APIGW-API-KEY': self.client_secret
        }
        super(summaryAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        summaries = []
        for item in args['content']:
            content_parts = [
                f"제목은 {item.get('stitle')}입니다." if item.get('stitle') else '',
                f"시작일은 {item.get('start')[11:16]}입니다." if item.get('start') else '',
                f"마감일은 {item.get('end')[11:16]}입니다." if item.get('end') else '',
                f"{self.getCalLabel(item.get('cal'))}은 {item.get('seat')}{item.get('sexer')}입니다." if item.get('cal') else '',
                item.get('scontent') if item.get('scontent') else '',
                f"출발지는 {item.get('sarea')}입니다." if item.get('sarea') else '',
                f"목적지는 {item.get('sdest')}입니다." if item.get('sdest') else '',
                f"메이트는 {item.get('smate')}입니다." if item.get('smate') else ''
            ]
            content_str = ' '.join(part for part in content_parts if part)  # 값이 있는 필드만 선택해 문자열로 변환합니다.
            print(content_str)
            data = {
                "document": {
                    "content": content_str  # 요약할 텍스트를 문자열로 넘겨줍니다.
                },
                "option": {
                    "language": "ko",
                    "model": "news",
                    "tone": 2,
                    "summaryCount": 3
                }
            }
            response = requests.post(self.url, headers=self.headers, data=json.dumps(data).encode('UTF-8'))
            summaries.append(response.json())
            print("요약 내용은?", summaries)

        return summaries

    @staticmethod
    def getCalLabel(cal):
        switcher = {
            1: '일정',
            2: '아침',
            3: '점심',
            4: '저녁',
            5: '운동',
            6: '경로'
        }
        return switcher.get(cal, '')
