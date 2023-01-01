#!/usr/bin/python3
import numpy as np
import time
import cv2
import cv2.aruco as aruco
import rospy
from std_msgs.msg import String
from std_msgs.msg import Float64
from PIL import Image
from yolo import YOLO
import threading
import sys
import os


class Detector:
    def __init__(self):
        rospy.on_shutdown(self.cleanup)
        self.yolo = YOLO()
        self.r = rospy.Rate(10)
        self.flag = False
        self.pub = rospy.Publisher("choose_path", String, queue_size=1)
        self.sub = rospy.Subscriber("end_speak", Float64, self.callback)
        self.jug = False
        self.jug2 = False
        self.jug3 = False
        self.status = 1
        self.max_detection = 0
        self.destination = 3  # 终点参数
        self.result = []
        self.cap = cv2.VideoCapture(0)
        weight = 416
        height = 416
        self.cap.set(3, weight)
        self.cap.set(4, height)
        self.detect()
        rospy.loginfo("All detection done.")
        self.speak()
        rospy.loginfo("Speaking done.")

    def detect(self):
        aruco_results = [0, 0, 0]
        t1 = 0
        while not rospy.is_shutdown():
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            if self.status == 1:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
                parameters = aruco.DetectorParameters_create()
                corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
                aruco.drawDetectedMarkers(frame, corners, ids)
                if ids is not None:
                    for i in range(len(ids)):
                        int_ids = int(ids[i])
                        if int_ids in [0, 1, 2]:
                            aruco_results[int_ids] += 1
                            if self.jug == False:
                                t1 = time.time()
                                self.jug = True

                t2 = time.time()
                if t1 != 0 and t2 - t1 > 1:  # 从检测到二维码到播报的时间间隔
                    if self.jug2 == False:
                        os.system("play ./audio/start.mp3")
                        if maxn == 1:
                            os.system("play ./audio/vegetable.mp3")
                        elif maxn == 2:
                            os.system("play ./audio/fruit.mp3")
                        else:
                            os.system("play ./audio/meat.mp3")
                        self.jug2 = True

                if t1 != 0 and t2 - t1 > 1.5:  # 从检测到二维码到出发的时间间隔
                    self.jug3 = True

                if ids is not None:
                    print(ids)
                    print(aruco_results)
                # print(aruco_results)
                maxn = 0
                for i in range(3):
                    maxn = i if aruco_results[i] > aruco_results[maxn] else maxn

                if self.jug3:
                    self.pub.publish(str(self.destination))
                    self.status = 2
                else:
                    self.pub.publish(str(100))
                self.r.sleep()
            elif self.status == 2:
                self.pub.publish(str(self.destination))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(np.uint8(frame))
                frame, res_class = self.yolo.detect_image(frame)
                if res_class and len(res_class) >= self.max_detection:
                    self.max_detection = len(res_class)
                    self.result = res_class
                print("detection:", res_class)
                print("result:", self.result)
                print("---------------------")
                if self.flag == True:
                    break

    def callback(self, data):
        self.flag = True

    def speak(self):
        speak_list = [0, 0]  # glasses, longhair
        if self.result:
            for i, element in enumerate(self.result):
                if element == "glass":
                    speak_list[0] += 1
                elif element == "hair":
                    speak_list[1] += 1
            speak_list[0] = min(speak_list[0], 2)
            speak_list[1] = min(speak_list[1], 2)
        os.system("play ./audio/final.mp3")
        os.system("play ./audio/total.mp3")
        os.system("play ./audio/%d.mp3" % speak_list[0])
        os.system("play ./audio/glasses.mp3")
        os.system("play ./audio/%d.mp3" % speak_list[1])
        os.system("play ./audio/long_hair.mp3")

    def cleanup(self):
        rospy.loginfo("Shutting down...")


if __name__ == '__main__':
    try:
        rospy.init_node("detector")
        rospy.loginfo("Detector node is started...")
        rospy.loginfo("Waiting for the message...")
        Detector()
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down detector node.")
        cv2.destroyAllWindows()