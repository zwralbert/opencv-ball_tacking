import cv2 as cv
import numpy as np
import serial
import os
import time

#设置静态变量  这里没有用到
def f():
    if not hasattr(f, 'x'):
        f.x = 0
    print(f.x)
    f.x += 1
#亮度和对比度调节函数 a是当前亮度背书，g加上的对比度
def contrast_brigthless_image(src1, a, g):
    h, w, ch = src1.shape
    src2 = np.zeros([h, w, ch], src1.dtype)
    dst = cv.addWeighted(src1, a, src2, 1 - a, g)
#实时监测球的位置
def ball_demo():
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 400)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 400)
    while True:
        char = ser.read(1)
        if char == b'3':
            break
        t1 = cv.getTickCount()
        ret, frame = cap.read()
        frame = cv.transpose(frame)
        frame = cv.flip(frame, 1)
        if ret == False:
            break
        src1 = frame[40:240, 40:230]
        hsv = cv.cvtColor(src1, cv.COLOR_BGR2HSV)
        lower_hsv = np.array([0, 0, 230])
        upper_hsv = np.array([180, 25, 255])
        mask = cv.inRange(hsv, lower_hsv, upper_hsv)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        sure = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel, iterations=2)
        mask = cv.dilate(sure, kernel, iterations=2)
        bin, contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for i, contour in enumerate(contours):
            mm = cv.moments(contour)
            cx = np.int(mm['m10'] / mm['m00'])
            cy = np.int(mm['m01'] / mm['m00'])
            x = ("{0} {1}".format(cx, cy))
            m = ser.write(x.encode('utf-8'))
            print(x)
        t2 = cv.getTickCount()
        fps1 = (t2 - t1) / cv.getTickFrequency()
        fps = 1 / fps1
        print(fps)
#从当前摄像头截取一张照片
def picture_demo():
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 400)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 400)
    while True:
        ret, frame = cap.read()
        frame = cv.transpose(frame)
        frame = cv.flip(frame, 1)
        src1 = frame[40:240, 40:230]
        cv.imwrite("0.jpg", src1)
        picture = cv.imread("0.jpg")
        break
    return picture


#根据截取的照片进行位置的标定
def demarcate_object(image):
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    lower_hsv = np.array([0, 0, 229])
    upper_hsv = np.array([180, 20, 255])
    mask = cv.inRange(hsv, lower_hsv, upper_hsv)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
    sure = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel, iterations=2)
    mask = cv.dilate(sure, kernel, iterations=2)
    dst = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
    bin, contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours):
        mm = cv.moments(contour)
        approx = cv.approxPolyDP(contour, 4, True)
        if approx.shape[0] > 3:
            cx = np.int(mm['m10'] / mm['m00'])
            cy = np.int(mm['m01'] / mm['m00'])
            x = ("{0} {1}".format(cx, cy))
            m = ser.write(x.encode('utf-8'))
            print(x)
    os.remove("0.jpg")

if __name__ == '__main__':
    while True:
        ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=0.5)#调用serial 模块进行与单片机通信
        x = '1,2'
        ser.write(x.encode('utf-8'))
        char=ser.read(1)
        if char==b'1': #接收数据然后进行标定
            picture=picture_demo()
            demarcate_object(picture)
        if char==b'2':#接收数据然后进行实时定位
            ball_demo()
