import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from flask_restful import Resource
from flask import request
import random
from basic_fuc import db_conn, query_insert, db_disconn, query_select

df = pd.read_csv('./api/megaGymDataset_.csv', encoding='ISO-8859-1')

df['Desc'] = df['Desc'].astype(str)
model = Word2Vec(sentences=df['Desc'],vector_size=100,window=5,min_count=1,sg=1)
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
        result_string = ', '.join(recommended_exercises)
        print('추천 받은 운동 :',recommended_exercises)

        connection = db_conn()

        for search_exercies in recommended_exercises:
            # 오늘 데이터를 불러와 NUM이 빠른 값을 찾음
            select_query = """
                    SELECT ID, E_NAME, ER_DATE, NUM
                    FROM EXERCISE_RECORD 
                    WHERE ID = :id AND TO_CHAR(er_date, 'YYYY-MM-DD') = TO_CHAR(SYSDATE, 'YYYY-MM-DD') 
                    ORDER BY NUM DESC
            """
            select_result = query_select(connection, query=select_query, id=id)
            print(select_result)

            if len(select_result) < 3:
                select_query_ = "SELECT COUNT(*) FROM EXERCISE_RECORD WHERE id = :id AND TO_CHAR(er_date, 'YYYY-MM-DD') = TO_CHAR(SYSDATE, 'YYYY-MM-DD') AND E_NAME = :E_NAME"
                select_result_ = query_select(connection, query=select_query_, id=id, E_NAME=search_exercies)
                if select_result_[0][0] == 0:
                    insert_query = "INSERT INTO EXERCISE_RECORD(id, e_name) VALUES (:id, :e_name)"
                    query_insert(connection, query=insert_query, id=id, e_name=search_exercies)
                    print('[행 삽입 완료]')
                else:
                    print('이미 오늘 추천 받았던 운동')
            else:
                print('[운동 업데이트]')
                # 가장 빠른 NUM 값을 가진 행을 업데이트하고, NUM은 신규 값으로 업데이트
                update_query = """
                    UPDATE EXERCISE_RECORD 
                    SET e_name = :new_e_name, NUM = :new_num 
                    WHERE id = :id AND NUM = (SELECT MIN(NUM) FROM EXERCISE_RECORD WHERE ID = :id AND TO_CHAR(ER_DATE, 'YYYY-MM-DD') = TO_CHAR(SYSDATE, 'YYYY-MM-DD')) 
                """
                query_insert(connection, query=update_query, new_e_name=search_exercies,
                             new_num=select_result[0][3] + 1, id=id)
                print('[업데이트 완료]')

        select_query = "SELECT count(*) FROM Schedule WHERE ID = :id AND TO_CHAR(Sch_Start, 'YYYY-MM-DD') = TO_CHAR(SYSDATE, 'YYYY-MM-DD') AND CALENDAR = 5 "
        select_result = query_select(connection, query=select_query, id=id)
        print("포인트 0번")
        if select_result[0][0] == 0:
            print("포인트 1번")
            insert_query = """INSERT INTO Schedule (ID, calendar, Sch_Title, Sch_exercise, Sch_Start, Sch_End)
                              VALUES (:id, 5, '운동 스케줄', :Sch_exercise, TRUNC(SYSDATE) + INTERVAL '20' HOUR, TRUNC(SYSDATE) + INTERVAL '21' HOUR)"""
            query_insert(connection, query=insert_query, id=id, Sch_exercise=result_string)
        else:
            print("포인트 2번")
            update_query = "UPDATE Schedule SET Sch_exercise = :Sch_exercise WHERE id = :id AND TO_CHAR(Sch_Start, 'YYYY-MM-DD') = TO_CHAR(SYSDATE, 'YYYY-MM-DD') AND CALENDAR = 5 "
            query_insert(connection, query=update_query, id=id, Sch_exercise=result_string)

        db_disconn(connection)

        return {'recommended_exercises': recommended_exercises}


def recommend(exercise_index):

    index_cosSim = list(enumerate(cos_sim[exercise_index]))
    index_cosSim_reverse = sorted(index_cosSim, key=lambda x: x[1], reverse=True)
    index_cosSim_reverse_top3 = index_cosSim_reverse[1:4]  #
    exercise_top3 = [idx[0] for idx in index_cosSim_reverse_top3]
    return df['Title'].iloc[exercise_top3]

