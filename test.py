from PIL import Image
from yolo import YOLO
import numpy as np
import time
import cv2
import os

yolo = YOLO()
for filename in range(2):
    img = cv2.imread("img/" + str(filename) + ".png")
    img = Image.fromarray(np.uint8(img))
    img, res_class = yolo.detect_image(img)
    img = np.asarray(img)
    #img = cv2.cvtColor(np.asarray(img),cv2.COLOR_BGR2RGB)
    cv2.imshow("img",img)
    cv2.waitKey(0)
