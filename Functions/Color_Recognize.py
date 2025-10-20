import sys
import os
import cv2
import math
import time
import numpy as np

import hiwonder.Camera as Camera
import hiwonder.Misc as Misc
import hiwonder.yaml_handle as yaml_handle

range_rgb = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),   # 注意：OpenCV中BGR，蓝色通道在开头
}

def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    areaMaxContour = None
    for c in contours:
        contour_area_temp = math.fabs(cv2.contourArea(c))
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 50:
                areaMaxContour = c
    return areaMaxContour, contour_area_max

lab_data = None
def load_config():
    global lab_data
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
load_config()

size = (320, 240)
def run(img):
    img_copy = img.copy()
    img_h, img_w = img.shape[:2]
    frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
    frame_gb = cv2.GaussianBlur(frame_resize, (3, 3), 3)
    frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)

    detected_colors = []

    # 循环处理三种颜色
    for color in ['red', 'green', 'blue']:
        if color not in lab_data:
            continue   # YAML中没有该颜色阈值就跳过

        # 获取该颜色的LAB阈值
        min_lab = tuple(lab_data[color]['min'])
        max_lab = tuple(lab_data[color]['max'])

        frame_mask = cv2.inRange(frame_lab, min_lab, max_lab)
        eroded = cv2.erode(frame_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        dilated = cv2.dilate(eroded, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        contours = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]

        areaMaxContour, area_max = getAreaMaxContour(contours)
        if areaMaxContour is not None and area_max > 200:
            ((centerX, centerY), radius) = cv2.minEnclosingCircle(areaMaxContour)
            centerX = int(Misc.map(centerX, 0, size[0], 0, img_w))
            centerY = int(Misc.map(centerY, 0, size[1], 0, img_h))
            radius = int(Misc.map(radius, 0, size[0], 0, img_w))
            draw_color = range_rgb[color]

            if radius > 1:
                cv2.circle(img, (centerX, centerY), radius, draw_color, 2)
                cv2.putText(img, "Color: " + color, (centerX - 30, centerY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)
                cv2.putText(img, f"Pos:({centerX},{centerY})", (centerX - 30, centerY + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)

    # 标记所有发现的颜色
    if detected_colors:
        cv2.putText(img, "Detected: " + ', '.join(detected_colors), (10, img.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return img

if __name__ == '__main__':
    from CameraCalibration.CalibrationConfig import *

    param_data = np.load(calibration_param_path + '.npz')
    mtx = param_data['mtx_array']
    dist = param_data['dist_array']
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

    open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
    if open_once:
        my_camera = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
    else:
        my_camera = Camera.Camera()
        my_camera.camera_open()
        
    print("Color_Recognize Init")
    print("Color_Recognize Start")
    while True:
        ret, img = my_camera.read()
        if img is not None:
            frame = img.copy()
            frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
            Frame = run(frame)
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        else:
            time.sleep(0.01)
    my_camera.camera_close()
    cv2.destroyAllWindows()
