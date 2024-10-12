
import cv2
import numpy as np


import cv2


def detect_tie(image_path):
    # 이미지 로드 및 이진화
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 이미지 중심점
    w = img.shape[1] // 2

    # 초기화
    curve = 0
    coordinate_list = []

    for h in range(0, img.shape[0]):
        if img[h, w] == 0:  # tie 영역 시작점 찾음
            coordinate_list.append((h, w))
            start_h = h
            w -= 1
            while w >= 0 and img[h, w] == 0:
                # curve 계산
                curve += 1
                if curve > 5:
                    break
                h -= 1

            if curve <= 5:
                while img[h, w] == 0 and h >= 0:
                    h -= 1
                h += 1

                # tie 영역인지 판단
                if len(coordinate_list) > 10:
                    x, y = zip(*coordinate_list)
                    fit = np.polyfit(y, x, 2)
                    if fit[0] < -0.001:
                        return True

            # 초기화
            curve = 0
            coordinate_list = []
            w = img.shape[1] // 2
            h = start_h
            w += 1

    return False

import math


def is_semicircle(coord_list):
    coord_list.sort()
    x_len = coord_list[-1][0] - coord_list[0][0]
    y_len = max(coord_list, key=lambda x: x[1])[1] - min(coord_list, key=lambda x: x[1])[1]
    radius = x_len / 2

    center = (coord_list[0][0] + radius, min(coord_list, key=lambda x: x[1])[1] + radius)
    start_angle = math.degrees(math.atan2(center[1] - coord_list[0][1], coord_list[0][0] - center[0]))
    end_angle = math.degrees(math.atan2(center[1] - coord_list[-1][1], coord_list[-1][0] - center[0]))
    if end_angle < start_angle:
        start_angle, end_angle = end_angle, start_angle

    for coord in coord_list:
        if not is_in_semicircle(center, radius, start_angle, end_angle, coord):
            return False

    return True


def is_in_semicircle(center, radius, start_angle, end_angle, point):
    dist = math.sqrt((center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2)
    if dist > radius:
        return False

    angle = math.degrees(math.atan2(center[1] - point[1], point[0] - center[0]))
    if start_angle <= angle <= end_angle:
        return True

    return False


result = detect_tie('C:\\Users\\LJW\\Downloads\\sheet_to_game\\sheet_test\\cut_slur_img.jpg')