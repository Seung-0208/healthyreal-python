import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from basic_fuc import db_conn, query_insert, db_disconn, query_select
from flask_restful import Resource
from flask import request
from datetime import datetime, timedelta
import json

class food_recommend(Resource):
    def post(self):
        # db 연결
        connection = db_conn()
        userid = request.json['id']
        meal_type = request.json['아침']
        user_meals = data_Integration(connection, userid)
        recommended_food = recommend_meal(user_meals, meal_type)
        db_disconn(connection)
        # return json.dumps({"recommended_food": recommended_food}, ensure_ascii=False), 200
    def get(self):
        # db 연결
        connection = db_conn()
        userid = request.args.get('id')
        meal_types = ['아침', '점심', '저녁']
        recommended_foods = []
        for meal_type in meal_types:
            user_meals = data_Integration(connection, userid)
            recommendation = recommend_meal(user_meals, meal_type)
            recommended_food = recommendation['RECOMMEND_FOOD']
            recipe_code = recommendation['RECIPECODE']
            recommended_foods.append({'MEAL_TYPE': meal_type, 'RECOMMEND_FOOD': recommended_food, 'RECIPECODE': recipe_code})

            db_save(connection, userid, meal_type, recommended_food, recipe_code)

        db_disconn(connection)
        print('추천된 음식 :', recommended_foods)
        # return json.dumps({"recommended_foods": recommended_foods}, ensure_ascii=False), 200

def data_Integration(connection, userid):
    # 어제의 날짜 계산
    # 오늘 날짜
    today = datetime.now().date()
    # 어제 날짜
    yesterday = today - timedelta(days=1)
    # YYYY-MM-DD 형식의 문자열로 변환
    yesterday_date = yesterday.strftime('%Y-%m-%d')
    # 레시피와 재료 테이블을 조인한 결과를 데이터프레임으로 가져옴
    recipe_ingredients_df = pd.read_sql_query("""select fl.category,fl.foodname,r.recipecode,ri.ingredient from foodlist fl 
                                                    join recipe r on fl.foodname = r.foodname 
                                                    join recipe_ingredients ri on r.recipecode = ri.recipecode""", connection)

    # 레시피별로 그룹화하여 재료를 리스트로 변환
    recipe_ingredients_grouped = recipe_ingredients_df.groupby(['RECIPECODE', 'FOODNAME'])['INGREDIENT'].apply(list).reset_index()

    # 사용자가 먹은 음식 데이터 (전일 먹었던 음식 데이터는 전부 제외)
    user_meals_df = pd.read_sql_query(f"""SELECT er.*, r.recipe_title, fl.category, ri.ingredient 
                                                FROM eating_record er
                                                JOIN recipe r ON er.eating_recipecode = r.recipecode
                                                JOIN foodlist fl ON er.eating_foodname = fl.foodname
                                                JOIN recipe_ingredients ri ON er.eating_recipecode = ri.recipecode
                                                WHERE er.id = '{userid}'
                                                AND er.eating_foodname NOT IN (
                                                    SELECT eating_foodname 
                                                    FROM eating_record 
                                                    WHERE id = 'rotkrlhh' 
                                                    AND TO_CHAR(EATING_DATE, 'YYYY-MM-DD') = TO_DATE('{yesterday}', 'YYYY-MM-DD')
                                                )""", connection)

    # 사용자가 먹은 음식 데이터를 딕셔너리로 변환
    user_meals = user_meals_df.to_dict(orient='records')

    return user_meals


import numpy as np  # numpy 추가

# 추천 함수
def recommend_meal(user_meals, meal_type):
    # meal_type에 따라 해당하는 음식 데이터를 추출
    filtered_user_meals = [meal for meal in user_meals if meal['MEALTYPE'] == meal_type]

    # 음식 데이터를 벡터화할 때 사용할 재료 추출
    ingredients = set()
    for meal in filtered_user_meals:
        ingredients.update(meal['INGREDIENT'])

    # 중복 재료 제거 후 인덱스 매핑
    ingredient_to_idx = {ingredient: idx for idx, ingredient in enumerate(ingredients)}

    # 음식 벡터화
    meal_vectors = []
    for meal in filtered_user_meals:
        # 'INGREDIENT' 키에 대한 값이 비어 있는 경우 건너뜁니다.
        if not meal['INGREDIENT']:
            continue
        vector = [0] * len(ingredients)
        for ingredient in meal['INGREDIENT']:
            vector[ingredient_to_idx[ingredient]] = 1
        meal_vectors.append(vector)

    # 음식 간 유사도 계산
    if len(meal_vectors) > 0:  # meal_vectors가 비어 있는지 확인
        similarities = cosine_similarity(meal_vectors, meal_vectors)
    else:
        similarities = np.zeros((0, 0))  # 비어 있는 경우 빈 유사도 행렬 생성

    # 추천할 음식 선택
    meal_scores = [0] * len(filtered_user_meals)
    for idx, meal in enumerate(filtered_user_meals):
        for similar_idx, similarity_score in enumerate(similarities[idx]):
            meal_scores[similar_idx] += similarity_score

    max_score_idx = meal_scores.index(max(meal_scores))
    recommended_food = {
        'RECOMMEND_FOOD': filtered_user_meals[max_score_idx]['EATING_FOODNAME'],
        'RECIPECODE': filtered_user_meals[max_score_idx]['EATING_RECIPECODE']
    }
    return recommended_food


def db_save(connection, userid, meal_type, RECOMMEND_FOOD,RECIPECODE):
    select_query = "SELECT COUNT(*) FROM EATING_RECORD WHERE ID = :userid AND MEALTYPE = :meal_type AND TRUNC(eating_date) = TRUNC(SYSDATE)"
    select_result = query_select(connection, query=select_query, userid=userid, meal_type=meal_type)
    if select_result[0][0] == 0:
        insert_query = "INSERT INTO EATING_RECORD(ID, MEALTYPE, EATING_FOODNAME, EATING_RECIPECODE, EATING_DATE) VALUES(:userid, :meal_type, :recommend_food, :recipe_code, SYSDATE)"
        query_insert(connection, query=insert_query, userid=userid, meal_type= meal_type, recommend_food= RECOMMEND_FOOD, recipe_code= RECIPECODE)