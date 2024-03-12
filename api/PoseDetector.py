from flask import jsonify, request
from flask_restful import Resource
import cv2
from ultralytics import YOLO
import os
import yt_dlp
import numpy as np

class PoseDetector(Resource):
    def __init__(self):
        # YOLOv8 모델을 초기화합니다. 'pose.pt'는 커스텀 학습된 모델 파일 경로입니다.
        self.model = YOLO('pose.pt')

    def download_video(self, url, output_path):
        ydl_opts = {
            'format': 'bestvideo',
            'outtmpl': output_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def process_frame_for_pose(self, frame):
        results = self.model(frame)
        keypoints = None
        # 키포인트 추출 로직 (YOLOv8 구현에 따라 다를 수 있음)
        if hasattr(results, 'keypoints'):
            keypoints = results.keypoints
        return keypoints

    def compare_poses(self, pose1, pose2):
        # 두 포즈 사이의 유사도를 계산합니다.
        # 이 예시에서는 단순히 포즈 벡터 간의 유클리드 거리를 사용합니다.
        # 실제 구현에서는 포즈 비교를 위한 더 복잡한 메트릭을 사용할 수 있습니다.
        dist = np.linalg.norm(pose1 - pose2)
        similarity = np.exp(-dist)  # 거리가 작을수록 유사도가 높습니다.
        return similarity

    def calculate_pose_similarity(self, keypoints1, keypoints2):
        # 포즈 유사도 계산 (키포인트 간 거리 및 각도 고려)
        # 이 부분은 프로젝트의 요구 사항에 맞게 구체적으로 구현해야 합니다.
        # 예제로, 두 키포인트 집합 간의 간단한 거리 유사도를 계산합니다.
        if keypoints1 is None or keypoints2 is None:
            return 0
        distance_sum = 0
        for kp1, kp2 in zip(keypoints1, keypoints2):
            distance_sum += np.linalg.norm(kp1 - kp2)
        similarity = np.exp(-distance_sum)  # 예시: 거리에 기반한 유사도
        return similarity

    def capture_and_compare(self, video_path):
        cap_downloaded = cv2.VideoCapture(video_path, cv2.CAP_DSHOW)
        cap_webcam = cv2.VideoCapture(0)  # 웹캠

        # 비디오의 FPS를 기반으로 5초마다 프레임을 처리합니다.
        fps_downloaded = cap_downloaded.get(cv2.CAP_PROP_FPS)
        fps_webcam = cap_webcam.get(cv2.CAP_PROP_FPS)
        # 두 비디오 중 더 낮은 FPS를 기준으로 삼아, 5초마다의 프레임 인덱스를 계산합니다.
        frame_interval = int(min(fps_downloaded, fps_webcam) * 5)

        frame_count = 0
        similarities = []  # 유사도를 저장하는 리스트
        while True:
            ret_downloaded, frame_downloaded = cap_downloaded.read()
            ret_webcam, frame_webcam = cap_webcam.read()

            if not ret_downloaded or not ret_webcam:
                break  # 둘 중 하나의 비디오가 끝나면 중단

            if frame_count % frame_interval == 0:
                keypoints_downloaded = self.process_frame_for_pose(frame_downloaded)
                keypoints_webcam = self.process_frame_for_pose(frame_webcam)
                similarity = self.calculate_pose_similarity(keypoints_downloaded, keypoints_webcam)
                similarities.append(similarity)  # 유사도를 리스트에 추가
                current_time = frame_count / min(fps_downloaded, fps_webcam)
                print(f"Time: {current_time:.2f}s, Similarity: {similarity:.4f}")

            frame_count += 1

        cap_downloaded.release()
        cap_webcam.release()

        # 유사도 리스트의 평균을 계산하여 반환합니다.
        avg_similarity = np.mean(similarities) if similarities else 0
        return avg_similarity

    def post(self):
        video_url = request.json['video_url']
        video_path = os.path.join('static', 'downloaded_video.mp4')
        self.download_video(video_url, video_path)
        avg_similarity = self.capture_and_compare(video_path)
        return jsonify({'average_similarity': avg_similarity})
