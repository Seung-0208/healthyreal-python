import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from flask_restful import Resource
from flask import request
import random
from wrtnai_crawling import wrtnCrawling
from basic_fuc import db_conn, query_insert, db_disconn, query_select

df = pd.read_csv('./api/megaGymDataset.csv', encoding='ISO-8859-1')

model = Word2Vec(sentences=df['BodyPart'],vector_size=100,window=5,min_count=1,sg=1)
word_vectors_matrics = model.wv.vectors.astype('float32')
title_to_index = dict(zip(df['Title'],df.index))
index_to_title = dict(zip(df.index,df['Title']))
cos_sim = cosine_similarity(word_vectors_matrics)

class recommendExercise(Resource):
    def post(self):
        # 뷰에서 넘긴 메세지 받기
        id = request.json['id']
        print('들어온 사용자 ID : ', id)
        content = request.json['message']
        print("사용자한테 받은 값",content)
        # 받은 메세지에 따라 다른 BodyPart를 가진 운동의 인덱스 찾기
        if content == 'Shoulders':
            bodyparts = ['Shoulders', 'Traps']
        elif content == 'arms':
            bodyparts = ['Biceps', 'Forearms', 'Triceps']
        elif content == 'legs':
            bodyparts = ['Calves', 'Adductors', 'Quadriceps', 'Hamstrings']
        elif content == 'Back':
            bodyparts = ['Lats', 'Lower Back', 'Middle Back']
        elif content == 'randam':
            bodyparts = df['BodyPart'].unique().tolist()  # 모든 BodyPart 중에서 선택
        else:
            bodyparts = [content]

        # 선택된 BodyPart 중에서 랜덤하게 하나 선택
        selected_bodypart = random.choice(bodyparts)

        # 선택된 BodyPart의 인덱스 찾기
        exercise_index = df[df['BodyPart'] == selected_bodypart].index[0]

        # 해당 인덱스를 사용해 추천 운동 찾기
        recommended_exercises = recommend(exercise_index).tolist()
        print('추천 받은 운동 :',recommended_exercises)

        # connection = db_conn()
        #
        # # # 추천된 각 운동에 대해 검색을 수행하고 결과를 모으기
        # # wrtn_results = []
        # #
        # # for search_exercies in recommended_exercises:
        # #     # wrtnCrawling() 함수를 호출하여 사용하고 검색어를 전달
        # #     search = '안녕하세요 혹은 인사, 추임새, 알겠습니다 하지말고' + search_exercies + '운동에 대해서만 하는 방법과 팁을 설명해줘'
        # #     wrtn_crawler = wrtnCrawling()
        # #     result = wrtn_crawler.get(search)
        # #     wrtn_results.append(result)
        # #
        # #     select_query = "SELECT COUNT(*) FROM EXERCISE_RECORD WHERE id = :id AND TO_CHAR(er_date, 'YYYY-MM-DD') = TO_CHAR(SYSDATE, 'YYYY-MM-DD') AND er_name = :er_name"
        # #     select_result = query_select(connection, query=select_query, id=id,er_name=search_exercies)
        # #     print(select_result)
        # #
        # #     if select_result[0][0] == 0:
        # #         insert_query = "INSERT INTO EXERCISE_RECORD(id, er_type, er_name, er_content) VALUES (:id, :er_type, :er_name, :er_content)"
        # #         query_insert(connection, query=insert_query, id=id, er_type=content, er_name=search_exercies, er_content=result)
        # #         print('[행 삽입 완료]')
        # #     else:
        # #         print('[오늘의 운동 추천은 끝]')
        # #
        # # print('뤼튼 검색 후 답변 모음 :', wrtn_results)
        # #
        # # returnDate = {
        # #     'recommended_exercises': recommended_exercises,
        # #     'wrtn_results': wrtn_results,
        # # }
        # #
        # # db_disconn(connection)

        return {'recommended_exercises': recommended_exercises}


def recommend(exercise_index):

    index_cosSim = list(enumerate(cos_sim[exercise_index]))
    index_cosSim_reverse = sorted(index_cosSim, key=lambda x: x[1], reverse=True)
    index_cosSim_reverse_top3 = index_cosSim_reverse[1:4]  #
    exercise_top3 = [idx[0] for idx in index_cosSim_reverse_top3]
    return df['Title'].iloc[exercise_top3]

