import cv2
import numpy as np
from ultralytics import YOLO
from scipy.spatial.distance import cosine
from PIL import ImageFont, ImageDraw, Image


def calculate_cosine_similarity(kp1, kp2):
    print("kp1 배열이 비어있어??", kp1)
    print("kp2 배열이 비어있어??", kp2)
    # 두 키포인트 배열의 길이가 같은지 확인
    if len(kp1) != len(kp2) or len(kp1) == 0:
        return 0  # 키포인트 배열이 비어 있거나 길이가 다르면 유사도를 0으로 처리

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

        for kp in kp_data[0]:  # 첫 번째 검출된 객체에 대한 모든 키포인트를 순회합니다.
            x, y, conf = kp  # 각 키포인트에서 x, y 좌표와 신뢰도(confidence)를 추출합니다.
            if conf > 0.3:  # 신뢰도가 0.3 이상인 키포인트만을 사용합니다.
                keypoints.append([x.item(), y.item()])
                confidences.append(conf.item())

    return np.array(keypoints), np.array(confidences)


def display_pose_accuracy(frame, accuracy):
    text = f"자세 정확도: {accuracy :.2f}"

    # OpenCV 이미지를 PIL 이미지로 변환합니다.
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)

    # 한글 폰트 지정 (폰트 파일 경로와 사이즈를 지정합니다. 시스템에 설치된 폰트 경로를 사용하세요.)
    font_path = "C:/Windows/Fonts/gulim.ttc"  # 폰트 경로 예시, 실제 경로로 변경 필요
    font = ImageFont.truetype(font_path, 20)

    # PIL 이미지에 텍스트를 그립니다.
    draw.text((10, 30), text, font=font, fill=(0, 255, 0))

    # PIL 이미지를 OpenCV 이미지로 다시 변환합니다.
    frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    return frame

def main():
    model = YOLO('E:/HMC/Project/Team_python/pose.pt')

    cap_webcam = cv2.VideoCapture(0)
    cap_video = cv2.VideoCapture('E:/HMC/Project/Team_python/static/converted_20240312232504.mp4')

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
            results_webcam = model(frame_webcam)
            results_video = model(frame_video)

            keypoints_webcam, confidences_webcam = extract_keypoints_and_confidence(results_webcam)
            keypoints_video, confidences_video = extract_keypoints_and_confidence(results_video)

            similarity = calculate_cosine_similarity(keypoints_webcam, keypoints_video)
            #display_pose_accuracy(frame_webcam, similarity)  # 웹캠 이미지에 정확도 표시

            # 자세 정확도를 이미지에 표시합니다.
            frame_webcam_with_accuracy = display_pose_accuracy(frame_webcam, similarity)
            # frame_video_with_accuracy = display_pose_accuracy(frame_video, similarity)  # 비디오 프레임에 적용할 경우

            cv2.imshow('Webcam Pose', frame_webcam_with_accuracy)
            #cv2.imshow('Webcam Pose', results_webcam[0].plot())
            cv2.imshow('Video Pose', results_video[0].plot())

        else:
            print('Failed to capture video.')
            break

        if cv2.waitKey(1) != -1:
            break

    cap_webcam.release()
    cap_video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
