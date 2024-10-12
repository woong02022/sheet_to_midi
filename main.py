import cv2
import mido

from find_staff import *
from change_image import *
from sort_symbol_list import *
from to_unreal import *
from finger_1 import *
from finger_2 import *
from octave_change import *
from pdf_to_image import *
from line_list import *
from create_midi import *
from cutting_img import *

scale_dic = [
    "c0", "d0", "e0", "f0", "g0", "a0", "b0",
    "c1", "d1", "e1", "f1", "g1", "a1", "b1",
    "c2", "d2", "e2", "f2", "g2", "a2", "b2",
    "c3", "d3", "e3", "f3", "g3", "a3", "b3",
    "c4", "d4", "e4", "f4", "g4", "a4", "b4",
    "c5", "d5", "e5", "f5", "g5", "a5", "b5",
    "c6", "d6", "e6", "f6", "g6", "a6", "b6",
    "c7", "d7", "e7", "f7", "g7", "a7", "b7",
    "c8", "d8", "e8", "f8", "g8", "a8", "b8",
]

"""
0 = 검은색, 255 = 흰색
"""

inputfolder = os.getcwd() + '\\input'
outputfolder = os.getcwd() + '\\output'

threshold = 0.7


def staff_line_interval(staff_lines):
    # 하나의 오선줄을 기준으로 평균을 정한다.
    r = 0
    a_1 = staff_lines[r + 1] - staff_lines[r]
    a_2 = staff_lines[r + 2] - staff_lines[r + 1]
    a_3 = staff_lines[r + 3] - staff_lines[r + 2]
    a_4 = staff_lines[r + 4] - staff_lines[r + 3]

    interval = round((a_1 + a_2 + a_3 + a_4) / 4)

    return interval


def name_to_number(is_str, name):
    """

    노트 , 쉼표의 이름으로 몇분음표 인지 판단 후
    그 속도를 숫자로 바꿔 내보낸다. (길수록 숫자가 커짐)
    """
    if name.find('quarter') >= 0:
        # 8th , 16th 일 수 있으므로
        if isinstance(is_str, str):
            if is_str == '4th':
                return 1
            if is_str == '8th':
                return 0.5
            elif is_str == '16th':
                return 0.25
            elif is_str == '32th':
                return 0.125
            elif is_str == '64th':
                return 0.0625
        else:
            return 1

    elif name.find('half') >= 0:
        return 2

    elif name.find('whole') >= 0:
        return 4


def combine_different_note_rest(result):
    """
    가끔보면 스템값이 다르지만 서로 같이 쳐야 되는 경우가 있다.
    예를 들면 4분음표와 2분음표가 서로 다른 스템값이지만 거의 동일 선상에 있어
    같이 쳐야 되는 경우

    위와 같은 경우는 4분음표로 처리를 해야하므로 더 빠른 쪽으로 합쳐버린다.
    기준은 노트헤드 가운데 가로폭(w 값 차이) 이 20 이하면 인정한다.
    """
    i = 0
    while True:
        if i == len(result) - 1:
            break
        else:
            if i == 0:
                # 제일 근처에 있는 노트 / 쉼표(0 부터 시작해서)
                i = find_near_right_note_or_rest(result, i)

            # 해당 노트의 w 값을 구한다.
            w_1 = result[i][0][0]
            try:
                stem_w_1 = result[i][0][5]
                # whole 노트 라면
                if stem_w_1 == 0:
                    stem_w_1 = 18000

            except IndexError:
                stem_w_1 = 18000

            # i 값에서 다음으로 근처에 있는 노트
            i_2 = find_near_right_note_or_rest(result, i)

            # 다음 노트가 존재하지 않다면 반복 종료
            if i_2 == 'none':
                break

            w_2 = result[i_2][0][0]
            try:
                stem_w_2 = result[i_2][0][5]
                if stem_w_2 == 0:
                    stem_w_2 = 9000

            except IndexError:
                stem_w_2 = 9000

            # 노트 헤드 w(가로폭) 값 차이가 20 미만 일때 아래 구문 실행
            # 서로 4th == 4th 일 경우도 실행된다는 거임
            if abs(w_1 - w_2) < 15:
                is_combine = False

                if result[i][0][2].find('rest') >= 0:
                    for n in range(0, len(result[i_2])):
                        if abs(result[i_2][n][1] - result[i][0][1]) <= 90:
                            is_combine = True
                            break

                elif result[i_2][0][2].find('rest') >= 0:
                    for n in range(0, len(result[i])):
                        if abs(result[i_2][0][1] - result[i][n][1]) <= 90:
                            is_combine = True
                            break

                else:
                    is_combine = True

                if is_combine is True:
                    for s in range(0, len(result[i_2])):
                        # i 번째에 합칠 i_2의 노트를 넣는다.
                        result[i].append(result[i_2][s])

                    result[i].sort(key=lambda x: x[1], reverse=True)
                    del result[i_2]

                else:
                    i = i_2
                    continue
            # 스템 w(가로폭) 값 차이가 15 미만 일때 아래 구문 실행
            elif abs(stem_w_1 - stem_w_2) < 15:
                for s in range(0, len(result[i_2])):
                    # i 번째에 합칠 i_2의 노트를 넣는다.
                    result[i].append(result[i_2][s])

                result[i].sort(key=lambda x: x[1], reverse=True)
                del result[i_2]

            elif result[i][0][2].find('whole') >= 0 and \
                result[i_2][0][2].find('whole') >= 0 and abs(w_1 - w_2) < 50:
                for s in range(0, len(result[i_2])):
                    # i 번째에 합칠 i_2의 노트를 넣는다.
                    result[i].append(result[i_2][s])

                result[i].sort(key=lambda x: x[1], reverse=True)
                del result[i_2]

            else:
                i = i_2
                continue

    return result


def delete_rest(result, staff_lines, staff_num):

    i = 0

    start = staff_lines[(5 * (staff_num - 1))]
    end = staff_lines[(staff_num * 5) - 1]

    while True:

        if i >= len(result):
            break
        # 합쳐지지 않은 쉼표만 거른다
        if result[i][0][2].find('rest') >= 0 and \
            len(result[i]) == 1:
            # 오선줄 안에 들어오지 않았다면 지운다
            if not start <= result[i][0][1] <= end:
                del result[i]

            else:
                i += 1

        else:
            i += 1

    return result


def detect_and_make_out(inputfolder, fn, bpm=60):
    """
      [음표(노트헤드)의 w 중간값 [0],
      음표의 h 중간값 [1],
      음표의 이름 [2],
      스템의 위 값 [3],
      스템 아랫 값 [4],
      스템 w 값 [5],
      음계 (octave 리스트)번호값 [6]
      음계 이름 [7]]

    """

    global make_1, result_1

    # 높이, 넓이, 이미지(흑 백 완벽 분리), 이미지(확인용 RGB 픽셀값)
    height, width, in_img, img_draw = \
        preprocess_img('{}/{}'.format(inputfolder, fn))

    # 스태프 높이 (h) 값 리스트
    staff_lines = get_staff_lines(width, height, in_img)

    # 스태프 거리 평균값 (아래 구하기 위해 사용)
    staff_interval = staff_line_interval(staff_lines)

    # 스태프와 스태프의 가운데 값
    half_staff_interval = round((staff_lines[1] - staff_lines[0]) / 2)

    # 음표 감지
    # True = 음표 감지 이미지 생성
    # False = 음표 감지 이미지 생성 x
    # make_image = T/F (모든 이미지 생성), make_c_image = T/F (합쳐진 이미지만 생성)
    all_symbol_tuple_list = final(in_img, img_draw, False, True)

    img_h, img_w = in_img.shape

    # 4분음표를 기준으로 몇초인지 알아내서 beat_second 라는 변수로 만듬
    beat_second = bpm_formula(bpm)
    # count bar 작업 시
    tempo = mido.bpm2tempo(bpm)
    # 이때 조표는 나중에 적용하게 되므로 겹세로줄의 정보를 all_symbol_tuple_list 에
    # 넣는 과정까지 필요할 듯

    # bar == 세로줄
    # bar_second == 한박의 길이
    # bpm 값까지 고려해 야 정확한 초가 나온다.
    # 사실상 bar_second 만 쓴다
    # end_line 은 나중에 slur 처리 시 쓰인다.
    # 나중에 겹세로줄, 도돌이표 등등의 탐지에 쓰일 예정이다. 
    bar_second, all_symbol_tuple_list = \
        find_bar_lines(in_img, staff_lines, img_w, all_symbol_tuple_list)

    # 음표를 좌표순으로 정리
    all_symbol_tuple_list.sort(key=lambda x: (x[0], x[1]))
    # 분류 마지막 스태프 작업 때 맨 하단 이미지까지 인식해야 완벽하게 될것이므로 이 정보도 안에 넣는다
    staff_lines.append(img_h)

    # 스태프 개수 만큼 반복
    staff_number = round(len(staff_lines) / 5)

    right_finger = []

    left_finger = []

    # [음표의 w 중간값, 음표의 h 중간값, 음표의 이름, 스템의 맨 위 값,
    # 스템 맨 아랫 값, 스템 w 값  음(리스트 번호), 음계]

    """ 
    result = 
         [음표의 w 중간값 [0],
         음표의 h 중간값 [1],
         음표의 이름 [2],
         스템의 위 값 [3],
         스템 아랫 값 [4],
         스템 w 값 [5],
         음계 (octave 리스트)번호값 [6]
         음계 이름 [7]]

       """
    # 다음 스태프 작업 시 첫 노트를 슬러 처리 할 것인가에 대한 여부
    right_slur_apply = False
    left_slur_apply = False

    last_octave = []
    l_last_octave = []
    r_last_octave = []

    # 한 오선줄 마다 반복
    for staff_num in range(1, staff_number + 2):

        # 1을 먼저 생성 후 진행하므로 짝수번호가 right 가 된다
        # result_2 (지금 만들려는) 는 짝수번호가 left 이다
        if staff_num % 2 == 0:
            hand = 'right'
            hand_2 = 'left'
            last_octave = l_last_octave

        else:
            hand = 'left'
            hand_2 = 'right'
            last_octave = r_last_octave

        # 맨 처음인 경우에는 오른손 먼저 처리
        # 다음이랑 비교해야 하기 때문에 먼저 오른손 사전 처리
        if staff_num == 1:
            result_1, right_slur_apply, left_slur_apply, last_octave = \
                process(staff_num, all_symbol_tuple_list, staff_lines, half_staff_interval, staff_interval, in_img,
                        img_h, 'right', right_slur_apply, left_slur_apply, last_octave)

            r_last_octave = last_octave

            continue

        if staff_num == staff_number + 1:
            if hand == 'right':
                right_finger.extend(result_1)

            elif hand == 'left':
                left_finger.extend(result_1)

            break

        else:
            result_2, right_slur_apply, left_slur_apply, last_octave = \
                process(staff_num, all_symbol_tuple_list, staff_lines, half_staff_interval, staff_interval, in_img,
                        img_h, hand_2, right_slur_apply, left_slur_apply, last_octave)

        if staff_num % 2 == 0:
            l_last_octave = last_octave
        else:
            r_last_octave = last_octave

        result_1, result_2 = distinguish_triplet(result_1, result_2, in_img, img_h,
                                                 staff_lines, staff_num)

        if hand == 'right':
            right_finger.extend(result_1)

        elif hand == 'left':
            left_finger.extend(result_1)

        result_1 = result_2

    for f in range(0, 2):
        if f == 0:
            finger = right_finger
        else:
            finger = left_finger

        # 엔진으로 보낼 txt 정리 시작
        final_list = start(finger, in_img)
        # key_signature, flat, sharp, 8va ...
        final_list = accept_octave(final_list)

        if f == 0:
            right_finger = final_list
        else:
            left_finger = final_list

    midi_file = create_midi_file(right_finger, left_finger, tempo)

    return right_final_list, left_final_list, beat_second, bar_second


def bpm_formula(val):
    """ bpm 공식
    val == bpm 값 을 넣으면 >> 4분음표 (기준)가 몇 초인지 나오게 된다.
     ex) bpm = 60  >> 4분음표 = 1초    1초 >> 60(기준) / 60(bpm 이 60이라면) = 1"""
    s = round(60 / val, 4)
    # mido의 bpm2tempo 공식과 똑같음
    # 밀리초 단위 인듯
    time = int(round((60 * 1000000) / val))
    time = mido.bpm2tempo(195)

    return s


def process(staff_num, all_symbol_tuple_list, staff_lines,
            half_staff_interval, staff_interval, in_img, img_h, hand,
            right_slur_apply, left_slur_apply, last_octave):
    """

    모든 음표를 감지한 그 정보로 확실하게 오선마다 나누게 한다.

    분류가 완료 되면 음계 정보도 넣고

    beam 감지로 8th, 16th 등의 정보를 넣고

    w 15 차이 내외 결합 , slur 감지도 한다.
    """
    result = sort_all(staff_num, all_symbol_tuple_list, staff_lines, half_staff_interval, staff_interval, in_img, img_h)
    # result == [노트헤드의 w 중간값[0], 노트헤드의 h 중간값[1], 음표의 이름[2],
    # 스템 h 맨 위 값[3], 스템 h 맨 아랫 값[4], 스템 w 값[5], 음(리스트 번호)[6], 음계[7]]

    # sort_all 에서 한번 진행하지만 whole 노트가 아직 안합쳐진 상태이고,
    # 노트 뿐만 아니라 쉼표도 같이 합쳐야 되기에 아래에서 진행한다
    # 2023.03.30 스템의 w 가 매우 가깝다면 또한 합친다
    result = combine_different_note_rest(result)

    # 적용되지 않는 rest 는 제거한다
    result = delete_rest(result, staff_lines, staff_num)

    # quarter note head 중 꼬리만을 인식해 빔 등을 찿아내 4th, 8th, 16th.. 등으로 구분한다.
    # 또한 여기서 dot 까지 적용을 시킨다
    result = make_dot_and_beam(result, in_img, img_h, staff_interval)

    # slur 적용
    # 적용된 note 는 rest 탈바꿈 혹은 멀티의 한 부분만 이라면 삭제 된다
    # right, left slur apply 는 그 전 오선줄에서 맨끝에 slur 가 적용된것을 보고
    # 다음 오선줄에서 처리 할 수 있도록 옥타브 정보를 남겨놓은 리스트이다.
    result, right_slur_apply, left_slur_apply, last_octave = \
        accept_slur(result, in_img, hand, right_slur_apply, left_slur_apply, last_octave)
    # =====================================================================

    return result, right_slur_apply, left_slur_apply, last_octave


def test_make_detect_image(inputfolder, fn, f, file_prefix):
    """
    테스트 할 symbol, note 등등의 감지된 이미지를 생성
    """
    height, width, in_img, img_draw = preprocess_img('{}/{}'.format(inputfolder, fn))

    # four_quarter_image(in_img, img_draw, file_prefix)

    # four_blank_image(in_img, img_draw, file_prefix)

    # coordinate = whole_note_head_detect(in_img)

    # coordinate = get_line_points_list([762, 916], [811, 903])

    # coordinate = [tuple(sublist) for sublist in coordinate]

    test_make_one_image(img_draw, coordinate, file_prefix, 1)


def main(bpm=60, go='none'):
    """

    :param go: none : 일반 처리 , test : 원하는 음표 인식 되는지 이미지 처리 및 생성
    :return:
    """
    try:
        # os.mkdir 은 파이썬에서 폴더를 생성할때 사용한다.
        # 즉 outputfolder 자체에 폴더를 생성한다.
        os.mkdir(outputfolder)
    except OSError as error:
        pass

    # 해당 경로의 파일/디렉토리명(리스트 형식)을 가져온다.
    list_of_images = os.listdir(inputfolder)

    right_finger = []
    left_finger = []
    beat_second = 0
    bar_second = 0

    # _ = 0, 1, 2 ..  fn = 00.png, 01.png ..
    # 안에 있는 파일을 하나씩 열거한다.
    for _, fn in enumerate(list_of_images):
        # Open the output text file #
        # 출력 텍스트 파일 열기

        # fn = 00.png >> fn.split('.') == [00, png]
        # file_prefix == 00
        file_prefix = fn.split('.')[0]
        # 00.txt 를 outputfolder 안에 만든다.
        # f로 변수로 저장해 언제든지 txt 에 쓸 준비를 한다.
        f = open(f"{outputfolder}/{file_prefix}.txt", "w")

        # 이미지를 개별적으로 처리
        try:
            if go == 'test':
                test_make_detect_image(inputfolder, fn, f, file_prefix)
            else:
                # 이미지를 잘라 인식시킬 이미지 개수를 늘린다
                # cutting_img(inputfolder, fn)

                right_finger, left_finger, beat_second, bar_second = \
                    detect_and_make_out(inputfolder, fn, bpm)

        except Exception:
            print('fail')
            pass

        # make_txt(right_finger, left_finger, beat_second, bar_second)

        f.close()

    print('Finished !!')

# pdf_2_image()

# main(0, 'test')

# change_pdf_dpi()

main(60)

