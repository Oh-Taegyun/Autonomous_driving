# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import YB_Pcb_Car

class driver:
    def __init__(self):
        self.y_value = 170  # 투시 변환 Y 기준 값
        self.detect_value = 100  # 이진화 임계값
        self.r_weight = 33  # 빨간색 가중치
        self.g_weight = 33  # 초록색 가중치
        self.b_weight = 33  # 파란색 가중치
        self.direction_threshold = 70000  # 방향 임계값
        self.up_threshold = 50000  # 직진 임계값
        self.motor_up_speed = 70 # 전진 속도
        self.motor_down_speed = 55  # 회전 속도
        self.brightness = 50
        self.contrast = 100
        self.saturation = 20
        self.gain = 20


    def weighted_gray(self, image, r_weight, g_weight, b_weight):
        r_weight /= 100.0  
        g_weight /= 100.0  
        b_weight /= 100.0  
        return cv2.addWeighted(cv2.addWeighted(image[:, :, 2], r_weight, image[:, :, 1], g_weight, 0), 1.0, image[:, :, 0], b_weight, 0)

    def process_frame(self, frame):
        cropped_frame = self.crop_frame(frame)
        gray_frame = self.weighted_gray(cropped_frame, self.r_weight, self.g_weight, self.b_weight)
        _, binary_frame = cv2.threshold(gray_frame, self.detect_value, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        binary_frame = cv2.morphologyEx(binary_frame, cv2.MORPH_CLOSE, kernel)
        binary_frame = cv2.morphologyEx(binary_frame, cv2.MORPH_OPEN, kernel)
        return binary_frame

    def crop_frame(self, frame):
        pts_src = np.float32([[90, 75+ self.y_value], [230,75+ self.y_value], [290, self.y_value], [30, self.y_value]])
        pts_dst = np.float32([[0, 240], [320, 240], [320, 0], [0, 0]])
        mat_affine = cv2.getPerspectiveTransform(pts_src, pts_dst)
        cropped_frame = cv2.warpPerspective(frame, mat_affine, (320, 240))
        for i in range(4):
            next_i = (i+1) % 4
            cv2.line(frame, tuple(pts_src[i]), tuple(pts_src[next_i]), (0, 0, 255), 2)
        return cropped_frame

    def decide_direction(self, histogram):
        length = len(histogram)
        DIVIDE_DIRECTION = 6
        left = int(np.sum(histogram[:length // DIVIDE_DIRECTION]))
        right = int(np.sum(histogram[(DIVIDE_DIRECTION-1) * length // DIVIDE_DIRECTION:]))
        center_left = int(np.sum(histogram[length // DIVIDE_DIRECTION: 3*length // DIVIDE_DIRECTION]))
        center_right = int(np.sum(histogram[3*length // DIVIDE_DIRECTION: 5*length // DIVIDE_DIRECTION]))
        if abs(right - left) > self.direction_threshold:
            return "LEFT" if right > left else "RIGHT"
        center = abs(center_left - center_right)
        if center < self.up_threshold:
            return "UP"

    def control_car(self, car, direction):
        if direction == "UP":  
            car.Car_Run(self.motor_up_speed, self.motor_up_speed)
        elif direction == "LEFT":  
            car.Car_Left(self.motor_down_speed , self.motor_up_speed+10)
            time.sleep(0.05)
            self.init_servo(car)
        elif direction == "RIGHT":  
            car.Car_Right(self.motor_up_speed+10, self.motor_down_speed)
            time.sleep(0.05)
            self.init_servo(car)
        else:  
            car.Car_Run(self.motor_up_speed, self.motor_up_speed)

    def rotate_servo(self, car, servo_id, angle):
        car.Ctrl_Servo(servo_id, angle)

    def init_camera(self, cap):
        cap.set(3, 320)
        cap.set(4, 240)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness)
        cap.set(cv2.CAP_PROP_CONTRAST, self.contrast)
        cap.set(cv2.CAP_PROP_SATURATION, self.saturation)
        cap.set(cv2.CAP_PROP_GAIN, self.gain)
        return cap

    def init_servo(self, car):
        self.rotate_servo(car, 1, 90)
        self.rotate_servo(car, 2, 120)

    def driving_direction(self, frame):
        processed_frame = self.process_frame(frame)
        histogram = np.sum(processed_frame, axis=0)
        direction = self.decide_direction(histogram)
        return direction

# car = YB_Pcb_Car.YB_Pcb_Car()
# cap = cv2.VideoCapture(0)
# cap.set(3, 320)
# cap.set(4, 240)
# driver_control = driver()
# driver_cap = driver_control.init_camera(cap)
# driver_control.init_servo(car)

# try:
#     while True:
#         ret, frame = driver_cap.read() 
#         if not ret:
#             car.Car_Stop()
#             continue

#         direction = driver_control.driving_direction(frame)
#         driver_control.control_car(car, direction)
#         cv2.imshow('1_Frame', frame)
#         cv2.imshow('2_binary__Frame', driver_control.process_frame(frame))
#         key = cv2.waitKey(30) & 0xff
#         if key == 27:
#             break

# except Exception as e:
#     print("Error occurred: {}".format(e))

# finally:
#     car.Car_Stop()
#     driver_cap.release()
#     cv2.destroyAllWindows()
