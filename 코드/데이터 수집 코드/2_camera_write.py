import cv2  # OpenCV 라이브러리: 영상 처리 및 컴퓨터 비전을 위한 라이브러리
import time  # 시간 측정 및 지연을 위한 라이브러리
import os  # 파일 및 디렉토리 조작을 위한 라이브러리
import numpy as np  # 배열 및 행렬 연산을 위한 라이브러리
from datetime import datetime  # 현재 날짜 및 시간을 얻기 위한 라이브러리
import YB_Pcb_Car  # Yahboom Pcb Car를 제어하기 위한 라이브러리

# 카메라 초기화
cap = cv2.VideoCapture(0)  # 카메라 객체 생성 (기본 카메라 사용)
cap.set(3, 320)  # 카메라 너비를 320으로 설정
cap.set(4, 240)  # 카메라 높이를 240으로 설정

# 트랙바 콜백 함수 (현재 사용되지 않음)
def nothing(x):
    pass

# Yahboom Pcb Car 객체 생성
car = YB_Pcb_Car.YB_Pcb_Car()

# 카메라 설정용 창 생성
cv2.namedWindow('Camera Settings')

# 트랙바(슬라이더) 생성
cv2.createTrackbar('Brightness', 'Camera Settings', 50, 100, nothing)  # 밝기 조절 트랙바
cv2.createTrackbar('Contrast', 'Camera Settings', 70, 100, nothing)  # 대비 조절 트랙바
cv2.createTrackbar('Saturation', 'Camera Settings', 70, 100, nothing)  # 채도 조절 트랙바
cv2.createTrackbar('Gain', 'Camera Settings', 80, 100, nothing)  # 감도 조절 트랙바
cv2.createTrackbar('R_weight', 'Camera Settings', 60, 100, nothing)  # R(빨강) 채널 가중치 조절 트랙바
cv2.createTrackbar('G_weight', 'Camera Settings', 60, 100, nothing)  # G(초록) 채널 가중치 조절 트랙바
cv2.createTrackbar('B_weight', 'Camera Settings', 10, 100, nothing)  # B(파랑) 채널 가중치 조절 트랙바

# 시작 시간 및 FPS 초기화
t_start = time.time()  # 시작 시간 기록
fps = 0  # FPS 초기화

# 가중치 기반 흑백 이미지 변환 함수
def weighted_gray(image, r_weight, g_weight, b_weight):
    sum_weight = r_weight + g_weight + b_weight  
    # 가중치를 0~1 사이 값으로 변환
    r_weight /= sum_weight
    g_weight /= sum_weight
    b_weight /= sum_weight
    # 각 채널에 가중치를 적용하여 흑백 이미지 생성
    return cv2.addWeighted(cv2.addWeighted(image[:, :, 2], r_weight, image[:, :, 1], g_weight, 0), 1.0, image[:, :, 0], b_weight, 0)

# Lab 색 공간에서 L, A, B 채널 분리 함수
def channel_frame(frame):
    lab_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)  # BGR 이미지를 Lab 색 공간으로 변환
    l_channel, a_channel, b_channel = cv2.split(lab_frame)  # L, A, B 채널 분리
    return l_channel, a_channel, b_channel

# 서보 모터를 제어하는 함수
def rotate_servo(car, servo_id, angle):
    car.Ctrl_Servo(servo_id, angle)  # Yahboom Pcb Car의 서보 모터 제어

# 트랙바에서 초기 서보 모터 각도 값을 가져옴
servo_1_angle = cv2.getTrackbarPos('Servo 1 Angle', 'Camera Settings')
servo_2_angle = cv2.getTrackbarPos('Servo 2 Angle', 'Camera Settings')

# 서보 모터 각도 초기화
rotate_servo(car, 1, 90)  # 서보 1을 90도로 회전
rotate_servo(car, 2, 113)  # 서보 2를 113도로 회전

# 메인 루프
while True:
    # 트랙바 값 읽기
    brightness = cv2.getTrackbarPos('Brightness', 'Camera Settings')  # 밝기 값
    contrast = cv2.getTrackbarPos('Contrast', 'Camera Settings')  # 대비 값
    saturation = cv2.getTrackbarPos('Saturation', 'Camera Settings')  # 채도 값
    gain = cv2.getTrackbarPos('Gain', 'Camera Settings')  # 감도 값
    r_weight = cv2.getTrackbarPos('R_weight', 'Camera Settings')  # 빨강 가중치
    g_weight = cv2.getTrackbarPos('G_weight', 'Camera Settings')  # 초록 가중치
    b_weight = cv2.getTrackbarPos('B_weight', 'Camera Settings')  # 파랑 가중치

    # 카메라 속성 설정
    cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
    cap.set(cv2.CAP_PROP_CONTRAST, contrast)
    cap.set(cv2.CAP_PROP_SATURATION, saturation)
    cap.set(cv2.CAP_PROP_GAIN, gain)

    # 카메라 프레임 읽기
    ret, frame = cap.read()

    # FPS 계산
    fps += 1
    mfps = fps / (time.time() - t_start)  # 평균 FPS

    # 원본 프레임 출력
    cv2.imshow('1 Step frame', frame)

    # 가중치를 적용한 흑백 프레임 생성 및 출력
    gray_frame = weighted_gray(frame, r_weight, g_weight, b_weight)
    cv2.imshow('2 Step weighted_gray_frame', gray_frame)

    # Lab 색 공간 채널 분리 (사용하지 않음)
    # l_channel, a_channel, b_channel = channel_frame(frame)
    # cv2.imshow('l_channel lab_frame', l_channel)
    # cv2.imshow('a_channel lab_frame', a_channel)
    # cv2.imshow('b_channel lab_frame', b_channel)

    # 키 입력 체크
    k = cv2.waitKey(30) & 0xff
    if k == 27:  # ESC 키를 누르면 루프 종료
        break

    if k == 32:  # SPACE 키를 누르면 사진 저장
        path = "./positive/rect_color_weight"  # 저장 경로
        if not os.path.exists(path):  # 경로가 없으면 생성
            os.makedirs(path)
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")  # 현재 시간 기록
        filename_gray = f"{path}/rect_gray_{timestamp}.jpg"  # 흑백 이미지 파일 이름
        filename_lab = f"{path}/rect_lab_{timestamp}.jpg"  # Lab 이미지 파일 이름
        print(f"images: {filename_gray} and {filename_lab} saved")  # 저장 메시지 출력
        cv2.imwrite(filename_gray, gray_frame)  # 흑백 이미지 저장
        # cv2.imwrite(filename_lab, l_channel)  # Lab 이미지 저장 (주석 처리됨)

    time.sleep(0.2)  # 0.2초 지연

# 리소스 해제
cap.release()  # 카메라 해제
cv2.destroyAllWindows()  # 모든 OpenCV 창 닫기
