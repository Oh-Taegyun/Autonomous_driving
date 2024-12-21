import cv2
import numpy as np
import time
import os
import YB_Pcb_Car

class DangerSign:
    def __init__(self, path):
        self.name = "rect"
        self.object_cascade = self.load_cascade(path)
        self.count = 0

        # 카메라 설정값 초기화
        self.brightness = 50
        self.contrast = 80
        self.saturation = 70
        self.gain = 80

        # RGB 가중치 설정
        self.r_weight = 33
        self.g_weight = 33
        self.b_weight = 33
        self.path = path

    def init_camera(self, cap):
        cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        cap.set(cv2.CAP_PROP_CONTRAST, self.contrast)
        cap.set(cv2.CAP_PROP_SATURATION, self.saturation)
        cap.set(cv2.CAP_PROP_GAIN, self.gain)
        return cap

    def load_cascade(self, path):
        cascade = cv2.CascadeClassifier()
        if not cascade.load(path):
            print(f'--(!)Error loading cascade: {path}')
            exit(0)
        return cascade

    def capture_frame(self, cap):
        ret, frame = cap.read()
        if not ret:
            print('--(!)Error capturing frame')
            return None
        return frame

    def weighted_gray(self, image):
        sum_weight = self.r_weight + self.g_weight + self.b_weight
        if sum_weight == 0:
            print("가중치 합이 0입니다. 기본값으로 초기화합니다.")
            self.r_weight, self.g_weight, self.b_weight = 33, 33, 34
            sum_weight = self.r_weight + self.g_weight + self.b_weight

        r_weight = self.r_weight / sum_weight
        g_weight = self.g_weight / sum_weight
        b_weight = self.b_weight / sum_weight

        return cv2.addWeighted(
            cv2.addWeighted(image[:, :, 2], r_weight, image[:, :, 1], g_weight, 0),
            1.0, image[:, :, 0], b_weight, 0
        )

    def detect_object_sign(self, frame):
        gray = self.weighted_gray(frame)
        object_sign = self.object_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return object_sign

    def draw_rectangles_and_text(self, frame, traffic_sign):
        for (x, y, w, h) in traffic_sign:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.putText(
                frame, f"{self.name}_({w}X{h})", (x - 30, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
            )
        return frame

# 디버그 코드
# cap = cv2.VideoCapture(0)
# cap.set(3, 320) 
# cap.set(4, 240) 

# # 위험 표시 감지 컨트롤러 셋팅
# path = '/home/pi/Desktop/OTG/final/stop_sign_classifier_2.xml'
# danger_sign_control = DangerSign(path)
# danger_sign_cap = danger_sign_control.init_camera(cap)

# while True:
#     ret, frame = danger_sign_cap.read()
#     if not ret:
#         continue

#     object_sign = danger_sign_control.detect_object_sign(frame)
#     print(object_sign)

#     if len(object_sign) > 0:
#         frame = danger_sign_control.draw_rectangles_and_text(frame, object_sign)
    
#     cv2.imshow("Detected Frame", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# danger_sign_cap.release()
# cv2.destroyAllWindows()
