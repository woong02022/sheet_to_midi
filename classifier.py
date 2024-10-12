import cv2
import numpy as np
import os
import copy
from threshold import *
from combine_one import *
import math

name_list = [
    'quarter_note_head',
    'half_note_head',
    'whole_note_head',
    # 'small_quarter_note_head',
    'sharp',
    'natural',
    'flat',
    'dot',
    'double_flat',
    'quarter_4th_rest',
    'quarter_8th_rest',
    'quarter_16th_rest',
    'quarter_32th_rest',
    'half_rest',
    'whole_rest',
    'treble_clef',
    'bass_clef',
    'treble_clef_inside',
    'bass_clef_inside',
    'triplet_3',
    'triplet_6',
    'va_8',
    'va_16',
    'vb_8',
    'vb_16',
    # 'slur',
    'bpm_start_4',
    'bpm_0',
    'bpm_1',
    'bpm_2',
    'bpm_3',
    'bpm_4',
    'bpm_5',
    'bpm_6',
    'bpm_7',
    'bpm_8',
    'bpm_9',


]


def middle_point(pt, h, w):
    a = (round((pt[0] + (pt[0] + w)) / 2), round((pt[1] + (pt[1] + h)) / 2))

    return a


def detect(comparion, read_img, threshold):
    before_pt = []

    # 해당 이미지가 없거나, 임계값을 설정 하지 않은 경우
    if read_img is None or threshold is None:
        return before_pt

    h, w = read_img.shape
    _, read_img = cv2.threshold(read_img, 200, 255, cv2.THRESH_BINARY)

    res = cv2.matchTemplate(comparion, read_img, cv2.TM_CCOEFF_NORMED)

    loc = np.where(res >= threshold)

    for i, pt in enumerate(zip(*loc[::-1])):

        a = middle_point(pt, h, w)
        if i == 0:
            before_pt.append(a)

        else:
            for r in range(0, len(before_pt)):
                if abs(a[0] - before_pt[r][0]) >= 12 or abs(a[1] - before_pt[r][1]) >= 12:
                    if len(before_pt) - r - 1 == 0:
                        before_pt.append(a)

                    else:
                        continue

                else:
                    break

    return before_pt


def size_set(staff_line):
    a = abs(staff_line[0] - staff_line[1])
    b = abs(staff_line[1] - staff_line[2])
    c = abs(staff_line[2] - staff_line[3])
    d = abs(staff_line[3] - staff_line[4])

    average_interval = round((a + b + c + d) / 4)  # 26

    result_h = average_interval + 2  # 28

    benchmark_h = 25

    benchmark_w = 30

    result_w = benchmark_w + (result_h - benchmark_h) * 3  # 39

    return result_h, result_w


def dot_detect(image, list, rgb, radius=10):
    """

    감지된 좌표에 점을 찍어준다.
    """
    dot_img = image
    if len(list) == 0:
        pass

    else:
        for i in range(0, len(list)):
            dot_img = cv2.circle(image, list[i], radius, rgb, -1)

    return dot_img


def make_all_symbol_tuple(tuple_list, name, all_symbol_tuple_list):
    for i in range(0, len(tuple_list)):
        tuple_to_list = list(tuple_list[i])
        tuple_to_list.append(name)
        list_to_tuple = tuple(tuple_to_list)
        all_symbol_tuple_list.append(list_to_tuple)

    return all_symbol_tuple_list


def final(image, img_draw, make_image=False, make_c_image=False, sheet_name='Sibelius'):
    all_symbol_tuple_list = []

    for i in range(0, len(name_list)):
        # 여러개를 중복으로 감지할 수 있으므로 전체적으로 확인하기 위한 이미지 값
        # ex 'quarter_note_head'
        current_name = name_list[i]
        a_d_img = copy.deepcopy(img_draw)

        new_list = []
        # 이미지 i 값
        img_i = 1
        while True:
            try:
                # threshold
                th = threshold[current_name]["%d" % img_i]
            except KeyError:
                break
            # musescore2 / Sibelius
            # Sibelius == symbol 폴더
            path = os.getcwd() + "\\musescore2\\%s\\%d.png" % (current_name, img_i)

            read_img = cv2.imread(path, 0)

            if read_img is None:
                break

            new_list, a_d_img = insert_list(
                image, read_img, th,
                new_list, make_image, img_draw,
                os.getcwd() + f"\\sheet_test\\%s_%d.png" % (current_name, img_i),
                a_d_img, "%s_%d" % (current_name, img_i))

            img_i += 1

        # 감지된 이미지를 모두 합친다
        if make_image is True:
            cv2.imwrite(os.getcwd() + f'\\sheet_test\\%s.jpg' % current_name, a_d_img)

        new_list = combine_detected(new_list, current_name)

        if make_c_image is True:
            a_d_img = copy.deepcopy(img_draw)
            for h in range(0, len(new_list)):
                w = new_list[h][0]
                h = new_list[h][1]

                a_d_img = cv2.circle(a_d_img, (w, h), 10, (0, 0, 255), -1)

            # 하나로 합쳐진 또다른 이미지를 출력
            cv2.imwrite(os.getcwd() + f'\\sheet_test\\%s_c.jpg' % current_name, a_d_img)

        all_symbol_tuple_list += new_list

    return all_symbol_tuple_list


# ============================================================

def test_make_one_image(image, coordinate, file_prefix, radius=10):
    """
    제대로 감지가 됬는지 테스트를 위해
    이미지에 점을 찍어서 출력하는 함수

    """
    # 감지된 좌표에 점을 찍어준다.
    # dot_detect(img_draw, 좌표, 점 색깔)
    dot_image = dot_detect(image, coordinate, (0, 255, 255), radius)

    cv2.imwrite(os.getcwd() +
                f'\\sheet_test\\jump_test\\detect_{file_prefix}.jpg', dot_image)


def insert_list(image, read_img, threshold, all_s_t_list,
                make_image, img_draw, out_path, a_d_img, name):

    detect_img = detect(image, read_img, threshold)

    all_s_t_list = make_all_symbol_tuple(detect_img, name, all_s_t_list)

    if make_image is True:
        raw_img = copy.deepcopy(img_draw)

        dot_image = dot_detect(raw_img, detect_img, (0, 0, 255), 8)

        a_d_img = dot_detect(a_d_img, detect_img, (0, 0, 255), 3)

        cv2.imwrite(out_path, dot_image)

    return all_s_t_list, a_d_img


def insert_list_2(image, read_img, threshold, all_s_t_list,
                make_image, img_draw, out_path, a_d_img, name):

    detect_img = []
    current_img = []
    resize_img = []

    for i in range(0, 40):
        # h 변화율이 w 변화율의 2배
        h, w = read_img.shape
        if 0 <= i <= 19:
            resize_img = cv2.resize(read_img, (h + i, math.trunc(w + i * 0.5)))

        elif 20 <= i <= 40:
            m = i - 19
            resize_img = cv2.resize(read_img, (h - m, math.trunc(w - m * 0.5)))

        detect_img = detect(image, resize_img, threshold)

        if i == 0:
            current_img = detect_img

        elif len(detect_img) > len(current_img):
            current_img = detect_img

    all_s_t_list = make_all_symbol_tuple(detect_img, name, all_s_t_list)

    if make_image is True:
        raw_img = copy.deepcopy(img_draw)

        dot_image = dot_detect(raw_img, detect_img, (0, 0, 255), 8)

        a_d_img = dot_detect(a_d_img, detect_img, (0, 0, 255), 3)

        cv2.imwrite(out_path, dot_image)

    return all_s_t_list, a_d_img
