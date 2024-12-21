import cv2
import numpy as np
import time
import os

import YB_Pcb_Car

class TriangleSign:
    def __init__(self):
        # 트랙바 값 초기화 (HSV 범위)
        self.h_min = 0
        self.h_max = 10
        self.s_min = 130
        self.s_max = 255
        self.v_min = 100
        self.v_max = 255

    def apply_histogram_equalization(self, src):
        src_ycrcb = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)
        ycrcb_planes = cv2.split(src_ycrcb)
        ycrcb_planes[0] = cv2.equalizeHist(ycrcb_planes[0])
        dst_ycrcb = cv2.merge(ycrcb_planes)
        dst = cv2.cvtColor(dst_ycrcb, cv2.COLOR_YCrCb2BGR)
        return dst

    def init_camera(self, cap):
        # cap = cv2.VideoCapture(0)
        # cap.set(3, 320)
        # cap.set(4, 240)
        return cap

    def detect_object_sign(self, frame):
        equalized_frame = self.apply_histogram_equalization(frame)
        canny_min = 100
        canny_max = 200
        min_area = 1000

        hsv = cv2.cvtColor(equalized_frame, cv2.COLOR_BGR2HSV)
        lower_red = np.array([self.h_min, self.s_min, self.v_min])
        upper_red = np.array([self.h_max, self.s_max, self.v_max])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        edges = cv2.Canny(mask, canny_min, canny_max)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

                if len(approx) == 3:
                    cv2.drawContours(equalized_frame, [approx], 0, (0, 255, 0), 2)
                    return True
        return False

# cap = cv2.VideoCapture(0)
# cap.set(3, 320)  # 너비 설정
# cap.set(4, 240)  # 높이 설정

# triangle_sign_control = TriangleSign()
# triangle_sign_cap = triangle_sign_control.init_camera(cap)

# while True:
#     ret, frame = triangle_sign_cap.read()
#     if not ret:
#         break
#     triangle_detect_sign = triangle_sign_control.detect_object_sign(frame)
#     cv2.imshow("Detected Frame", frame)
#     print(triangle_detect_sign)
#     if triangle_detect_sign:
#         print("Sign Detected! Stopping Car.")

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# triangle_sign_cap.release()
# cv2.destroyAllWindows()
