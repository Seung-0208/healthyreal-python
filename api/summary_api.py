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
        # 모든 항목을 포함할 큰 문자열을 초기화합니다.
        combined_content = []
        for item in args['content']:
            cal_label = self.getCalLabel(item.get('cal')) if item.get('cal') is not None else ''
            seat = item.get('seat', '') if item.get('seat') is not None else ''
            sexer = item.get('sexer', '') if item.get('sexer') is not None else ''
            seat_sexer_info = ''.join([seat, sexer]) if seat or sexer else ''
            cal_info_str = f"{cal_label}은 {seat_sexer_info}입니다." if cal_label and seat_sexer_info else ''

            content_parts = [
                f"제목은 {item.get('stitle', '')}입니다." if item.get('stitle') else '',
                f"시작일은 {item.get('start', '')[11:16]}입니다." if item.get('start') else '',
                f"마감일은 {item.get('end', '')[11:16]}입니다." if item.get('end') else '',
                cal_info_str,
                item.get('scontent', '') if item.get('scontent') else '',
                f"출발지는 {item.get('sarea', '')}입니다." if item.get('sarea') else '',
                f"목적지는 {item.get('sdest', '')}입니다." if item.get('sdest') else '',
                f"메이트는 {item.get('smate', '')}입니다." if item.get('smate') else ''
            ]
            content_str = ' '.join(part for part in content_parts if part)
            # 개별 항목 대신, 모든 항목을 하나의 큰 문자열로 추가합니다.
            combined_content.append(content_str)

        # 모든 항목을 포함하는 큰 문자열을 최종 생성합니다.
        final_content = ' '.join(combined_content)
        print(final_content)

        data = {
            "document": {
                "content": final_content
            },
            "option": {
                "language": "ko",
                "model": "general",
                "tone": 2,
                "summaryCount": 1
            }
        }
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data).encode('UTF-8'))
        summary = response.json() if response.ok else {'error': response.json()}
        print("요약 내용은?", summary)

        return summary

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
