import cv2
import threading
import time
import RPi.GPIO as GPIO
import sys
from driver import driver
from danger_sign import DangerSign
import numpy as np
import YB_Pcb_Car

# 경고음 함수
def beep_sound(frequency=440, duration=0.5):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(32, GPIO.OUT)
    try:
        p = GPIO.PWM(32, frequency)
        p.start(50)
        time.sleep(duration)
        p.stop()
    finally:
        GPIO.cleanup()

def beep_three_times():
    for _ in range(3):
        beep_sound()
        time.sleep(0.1)

def play_c_e_g():
    beep_sound(261.63, 0.5)  # 도(C4)
    time.sleep(0.1)
    beep_sound(329.63, 0.5)  # 미(E4)
    time.sleep(0.1)
    beep_sound(392.00, 0.5)  # 솔(G4)

# 경로 설정
path1 = "/home/pi/Desktop/OTG/final/stop_sign_classifier_2.xml"
path2 = "/home/pi/Desktop/OTG/final/ttri.xml"
path3 = "/home/pi/Desktop/OTG/final/oxox.xml"

# 객체 초기화
driver_control = driver()
danger_sign1 = DangerSign(path1)
danger_sign2 = DangerSign(path2)
danger_sign3 = DangerSign(path3)
car = YB_Pcb_Car.YB_Pcb_Car()
car.Ctrl_Servo(1, 90)
car.Ctrl_Servo(1, 120)

# 카메라 초기화
cap = cv2.VideoCapture(0)
cap = driver_control.init_camera(cap)


# 스레드 일시 중지 이벤트
pause_event = threading.Event()

# 스레드 종료 이벤트 생성
stop_event1 = threading.Event()
stop_event2 = threading.Event()
stop_event3 = threading.Event()
stop_event_drive = threading.Event()

def danger_sign_thread(danger_sign_control, shared_frame, car, stop_event):
    while not stop_event.is_set():
        if pause_event.is_set():
            time.sleep(0.1)
            continue
        
        frame_copy = shared_frame.copy()
        traffic_sign = danger_sign_control.detect_object_sign(frame_copy)
        if len(traffic_sign) > 0:
            print(f"Danger detected by {danger_sign_control.path}")
            if danger_sign_control == danger_sign1:
                
                car.Car_Stop()
                pause_event.set()
                beep_three_times()
                pause_event.clear()
                

            elif danger_sign_control == danger_sign2:
                car.Car_Stop()
                pause_event.set()
                play_c_e_g()
                pause_event.clear()
                
                
            elif danger_sign_control == danger_sign3:
                print("Parking - Stopping All Threads")
                x,y,w,h=traffic_sign[0]
                o_center = (x + w) // 2
                frame_x_center = 160
                if o_center < frame_x_center: 
                    stop_event_drive.set()
                    print("Parking - Stopping All Threads")
                    car.Car_Run(30, 100)
                    time.sleep(0.45)
                    car.Car_Run(40, 40)
                    time.sleep(1.35)
                    car.Car_Run(100, 30)
                else: 
                    stop_event_drive.set()
                    print("Parking - Stopping All Threads")
                    car.Car_Run(100, 30)
                    time.sleep(0.45)
                    car.Car_Run(40, 40)
                    time.sleep(1.35)
                    car.Car_Run(30, 100)
                stop_event_drive.set()
                print("Parking - Stopping All Threads")

                car.Car_Stop()
                time.sleep(10)
                stop_event1.set()
                stop_event2.set()
                stop_event3.set()
                sys.exit(0)  # 프로세스 종료

            time.sleep(2)
            stop_event.set()

def driving_thread(shared_frame, car, stop_event_drive):
    driver_control.init_servo(car)
    while not stop_event_drive.is_set():
        if pause_event.is_set():
            car.Car_Stop()
            time.sleep(0.1)
            continue

        ret, frame = cap.read()
        if not ret:
            car.Car_Stop()
            continue

        shared_frame[:] = frame.copy()
        direction = driver_control.driving_direction(frame)
        driver_control.control_car(car, direction)

# 공유 프레임 생성
shared_frame = np.zeros((240, 320, 3), dtype=np.uint8)

# 스레드 실행
thread1 = threading.Thread(target=danger_sign_thread, args=(danger_sign1, shared_frame, car, stop_event1))
thread2 = threading.Thread(target=danger_sign_thread, args=(danger_sign2, shared_frame, car, stop_event2))
thread3 = threading.Thread(target=danger_sign_thread, args=(danger_sign3, shared_frame, car, stop_event3))
thread_drive = threading.Thread(target=driving_thread, args=(shared_frame, car, stop_event_drive))

thread1.start()
thread2.start()
thread3.start()
thread_drive.start()

# 메인 스레드 대기
thread1.join()
thread2.join()
thread3.join()
thread_drive.join()

cap.release()
