from flask import request
from flask_restful import Resource
import os
import yt_dlp
import cv2
import numpy as np
from ultralytics import YOLO
from scipy.spatial.distance import cosine
from PIL import ImageFont, ImageDraw, Image

class PoseDetector(Resource):
    def __init__(self):
        # YOLOv8 모델을 초기화합니다. 'pose.pt'는 커스텀 학습된 모델 파일 경로입니다.
        self.model = YOLO('pose.pt')

    def post(self):
        video_url = request.json['video_url']
        video_path = os.path.join('static', 'downloaded_video.mp4')
        self.download_video(video_url, video_path)

        print("생성된 비디오 경로", video_path)

        #cap_webcam = cv2.VideoCapture(0)
        #cap_video = cv2.VideoCapture(video_path)
        cap_webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # DirectShow를 사용하여 웹캠 열기
        cap_video = cv2.VideoCapture(video_path, cv2.CAP_ANY)  # 가능한 모든 백엔드를 시도하여 비디오 열기

        # 비디오의 FPS를 조절하기 위한 변수 설정
        frame_interval = 5  # 15 FPS에 해당하는 간격을 조절하기 위해 사용
        frame_count = 0

        while True:
            ret_webcam, frame_webcam = cap_webcam.read()
            ret_video, frame_video = cap_video.read()

            # 프레임 간격 조절을 통해 FPS를 감소시킵니다.
            frame_count += 1
            if frame_count % frame_interval != 0:
                continue

            if ret_webcam and ret_video:
                results_webcam = self.model(frame_webcam)
                results_video = self.model(frame_video)

                keypoints_webcam, confidences_webcam = self.extract_keypoints_and_confidence(results_webcam)
                keypoints_video, confidences_video = self.extract_keypoints_and_confidence(results_video)

                similarity = self.calculate_cosine_similarity(keypoints_webcam, keypoints_video)
                self.display_pose_accuracy(frame_webcam, similarity)  # 웹캠 이미지에 정확도 표시

                # 자세 정확도를 이미지에 표시합니다.
                frame_webcam_with_accuracy = self.display_pose_accuracy(frame_webcam, similarity)
                # frame_video_with_accuracy = display_pose_accuracy(frame_video, similarity)  # 비디오 프레임에 적용할 경우

                print(f"자세 정확도: {similarity}")

                cv2.imshow('Webcam Pose', frame_webcam_with_accuracy)
                # cv2.imshow('Webcam Pose', results_webcam[0].plot())
                cv2.imshow('Video Pose', results_video[0].plot())

            else:
                print('Failed to capture video.')
                break

            if cv2.waitKey(1) != -1:
                break

        cap_webcam.release()
        cap_video.release()
        cv2.destroyAllWindows()

    def download_video(self, url, output_path):
        ydl_opts = {
            'format': 'bestvideo',
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])


    def calculate_cosine_similarity(self, kp1, kp2):
        if len(kp1) != len(kp2) or len(kp1) == 0:
            return 0

        # 코사인 유사도 계산
        kp1_flat = kp1.flatten()
        kp2_flat = kp2.flatten()
        similarity = 1 - cosine(kp1_flat, kp2_flat)

        # 코사인 유사도를 백분율로 변환
        percentage_similarity = similarity * 100

        return percentage_similarity

    def extract_keypoints_and_confidence(results):
        keypoints = []
        confidences = []
        if hasattr(results[0], 'keypoints') and results[0].keypoints is not None:
            kp_data = results[0].keypoints.data  # 키포인트 데이터

            for kp in kp_data[0]:
                x, y, conf = kp
                if conf > 0.3:  # 신뢰도가 0.3 이상.
                    keypoints.append([x.item(), y.item()])
                    confidences.append(conf.item())

        return np.array(keypoints), np.array(confidences)

    def display_pose_accuracy(frame, accuracy):
        text = f"자세 정확도: {accuracy :.2f}"

        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(frame_pil)

        font_path = "C:/Windows/Fonts/gulim.ttc"
        font = ImageFont.truetype(font_path, 20)

        # PIL 이미지에 텍스트를 그립니다.
        draw.text((10, 30), text, font=font, fill=(0, 255, 0))

        # PIL 이미지를 OpenCV 이미지로 다시 변환합니다.
        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

        return frame



