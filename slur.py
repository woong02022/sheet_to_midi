import copy

from classifier import *


def find_near_right_note(result, i):
    find_i = None
    while True:
        i += 1

        if i > len(result) - 1:
            find_i = 'none'
            break

        elif find_i is not None:
            break
        # rest 랑 note 가 합쳐진 경우가 있으므로
        # 합쳐진 모든 리스트를 훑어본다
        for s in range(0, len(result[i]) - 1):
            if result[i][s][2].find('note') >= 0:
                find_i = i
                break

    return find_i


def find_near_left_note(result, i):
    while True:
        i -= 1

        if i == -1:
            find_i = 'none'
            break

        elif find_i is not None:
            break

        # rest 랑 note 가 합쳐진 경우가 있으므로
        # 합쳐진 모든 리스트를 훑어본다
        for s in range(0, len(result[i])):
            if result[i][s][2].find('note') >= 0:
                find_i = i

    return find_i


def end_list(result, i):
    """
    해당 i 값에 있는 result 의 끝 노트를 찿는다

    8th 이나 triplet 등의 기호 등이 포함되 노
    트 자체의 정확한 뒤쪽을 모르기 때문
    """
    count = -1
    while True:
        if isinstance(result[i][count], list):
            break

        else:
            count -= 1

    return count


def accept_slur(result, in_img, hand,
                right_slur_apply, left_slur_apply, last_octave):

    """
    slur 의 적용 범위 예측 이미지를 선정해 잘라낸다.
    """
    i = 0
    is_same = {}

    before_note = []
    s = -1
    while True:
        if abs(s) == len(result):
            _, end_line = in_img.shape
            break

        elif result[s][0][2] == 'bar':
            end_line = result[s][0][0]
            break

        else:
            s -= 1

    # 아래가 둘다 true 라면 그 전 오선줄에 마지막 노트에서 slur 가 감지되었다는 뜻
    # 따라서 맨 처음 노트에 slur 를 적용
    if hand == 'right' and right_slur_apply is True:
        i = find_near_right_note(result, i)
        result = apply_slur(result, 0, i, [], last_octave)
        last_octave = []
        right_slur_apply = False


    elif hand == 'left' and left_slur_apply is True:
        i = find_near_right_note(result, i)
        result = apply_slur(result, 0, i, [], last_octave)
        last_octave = []
        left_slur_apply = False


    while True:
        # compare_list = [b4, e5, b5]
        compare_octave = []
        compare_octave_2 = []

        # 마지막까지 반복했을때
        # 마지막 줄 정보로 마지막에 slur 가 있는지 판단
        if i == 'none' or i >= len(result) or is_same == {'true'}:
            break

        elif result[i][0][2].find('note') >= 0 or len(before_note) >= 1:
            if len(before_note) >= 1:
                end = end_list(before_note, 0)
                for s in range(0, len(before_note[0]) + end + 1):
                    compare_octave.append(before_note[0][s][-1])

            else:
                end = end_list(result, i)
                # c4, d2 등 옥타브 만 따서 리스트 에 저장
                for s in range(0, len(result[i]) + end + 1):
                    compare_octave.append(result[i][s][-1])
            # 이 노트 다음에 노트가 있는지 확인
            i_2 = find_near_right_note(result, i)

            # end_line 값으로 끝에 slur 가 있는지 확인
            if i_2 == 'none':
                is_same = {'true'}

            else:
                end_2 = end_list(result, i_2)
                for n in range(0, len(result[i_2]) + end_2 + 1):
                    compare_octave_2.append(result[i_2][n][-1])

                # flat 일 경우 slur 감지 오류가 있을 수 있으니 방지
                # 아래 구문은 노트가 1개 이며 그전 flat 이 적용이 된다는 가정하에다
                if len(compare_octave_2) == 1 and \
                    result[i_2 - 1][0][2] == 'flat' and \
                    result[i_2][0][-1] == result[i_2 - 1][0][-1]:
                    is_same = {}

                else:
                    is_same = set(compare_octave) & set(compare_octave_2)

            # 같은 것이 하나 라도 있다면
            if is_same != set():

                # 잘려질 w(가로) 범위 값

                if len(before_note) >= 1:
                    x_1 = before_note[0][0][0] - 20

                else:
                    x_1 = result[i][0][0] - 20
                # 다음 노트가 없는 경우 마지막 라인에 slur 확인
                if is_same == {'true'}:
                    x_2 = end_line + 25

                else:
                    x_2 = result[i_2][0][0] + 20

                # 잘려질 h(세로) 범위 값 (자신의 값으로)
                if len(before_note) >= 1:
                    y_1 = before_note[0][end][1] - 50
                else:
                    y_1 = result[i][end][1] - 50

                if len(before_note) >= 1:
                    y_2 = before_note[0][0][1] + 50

                else:
                    y_2 = result[i][0][1] + 50


                cut_img = in_img[y_1:y_2, x_1:x_2]

                # 어떻게 이미지가 잘렸는지 제작 해서 보여주는 테스트 용 (없어도 무방)
                cv2.imwrite(os.getcwd() +
                            '\\sheet_test\\cut_slur_img.jpg', cut_img)

                # 슬러의 길이를 대충 계산
                # 슬러의 양쪽에 있는 노트 헤드 x값에 +23 여유를 두고 값을 구한다
                # 그리고 양쪽 값을 빼서 슬러의 x 길이를 유추한다.

                # 아까 자를 이미지 값 구할때 -20 해서 원상태 복구
                if len(before_note) >= 1:
                    x_1 = before_note[0][0][0] - 20

                else:
                    x_1 = result[i][0][0] - 20

                if is_same == {'true'}:
                    x_2 = end_line + 25
                else:
                    x_2 = result[i_2][0][0]


                is_slur = detect_slur(cut_img)

                # 감지가 됬다면
                if is_slur is True:
                    # 노트 자체가 완전 같다면
                    # slur 처리할 곳을 아예 rest 로 만들어 버린다. (slur 표시 한후 나중에 따로 처리됨)

                    # 마지막 노트와 세로줄 사이 이음줄 발견 시
                    # 다음 같은 음자리표 처리 시 처음 노트에 슬러를 적용시키는가
                    if is_same == {'true'}:
                        if hand == 'right':
                            right_slur_apply = True
                        elif hand == 'left':
                            left_slur_apply = True
                        # 마지막 옥타브를 비교하기 위해
                        last_octave = []
                        if len(before_note) >= 1:
                            for s in range(0, len(before_note[0])):
                                # 리스트 인지 판단해서 오류 안나게
                                if isinstance(before_note[0][s], list) is True:
                                    last_octave.append(before_note[0][s][-1])

                                else:
                                    continue

                        else:
                            for s in range(0, len(result[i])):
                                # 리스트 인지 판단해서 오류 안나게
                                if isinstance(result[i][s], list) is True:
                                    last_octave.append(result[i][s][-1])

                                else:
                                    continue

                    else:
                        next_before_note = []
                        next_before_note.append(copy.deepcopy(result[i_2]))
                        result = apply_slur(result, i, i_2, before_note)
                        before_note = next_before_note

                else:
                    before_note = []
            else:
                before_note = []

            i = i_2

        else:
            i += 1
            before_note = []


    return result, right_slur_apply, left_slur_apply, last_octave


def detect_slur(cut_img):
    """ 이미지를 잘보면 점점 올라가는 형태인데 이게
    갈수록 휘어지니까 위쪽 가운데에 점을 잡았다고 한다면
    좌측으로 이동할떄 현재 이동을 한 거리쯤에 1만큼 올라갔다면
    다시 그 거리만큼 이동을 했을떄 (+-3) 1 이상 만큼 올라가지 않았다면
    슬러로 인정하지 않는다 이때 겹치는 경우가 있을수 있으므로 (staff 등)

    그럼 굵기로 계속 해당 시작점으로 부터 count_0 로 픽셀을 센다음에
    굵기가 점점 얇아지는지, 위치가 커브성을 가지면서 바뀌는지 등을 보면서 해야할듯

    아래로 내려갈때랑 위로 올라갈때 2가지 검색 방법을 해야 할거같은데
    위로 올라갈때는 웃는 모양, 아래로 내려갈때는 그 반대를 검색해야 한다 """
    h, w = cut_img.shape

    is_slur = False
    # middle_w
    for p in range(0, 3):
        if is_slur is True:
            break

        elif p == 0:
            m_w = round(w / 2)

        elif p == 1:
            m_w = round(w / 2) - 7

        elif p == 2:
            m_w = round(w / 2) + 7

        is_slur = False
        direction = None
        start_h = 0

        coord_list = []
        while True:
            if start_h >= h:
                break
            # 검은색 픽셀 지점을 발견한 경우 slur 탐지를 시작
            elif cut_img[start_h][m_w] == 0:

                # 나중에 되돌릴 값을 미리 기억해두기 위해 h, w 값 저장
                start_1 = start_h
                find_middle_2 = start_h + 1
                i = 1
                while True:
                    if start_h + i >= h:
                        break

                    if cut_img[start_h + i][m_w] == 0:
                        i += 1
                    else:
                        find_middle_1 = start_h + i - 2
                        start_2 = start_h + i - 1
                        break
                if start_h + i >= h:
                    break

                else:
                    # 첫번째 반복은 위에서 아래로, 두번째 반복은 아래에서 위 방향
                    # 0, 1 방법은 커지는지 확인, 2, 3 방법은 작아지는지 확인
                    for s in range(0, 4):
                        # start_h 설정
                        # start_h 는 시작이 255 인 값에서 시작해야 하기 때문에
                        # 아래와 같이 설정

                        if s == 0 or s == 2:
                            start_h = find_middle_1

                        elif s == 1 or s == 3:
                            start_h = find_middle_2

                        i = 0
                        count = 0
                        # 일단 먼저 해야 할것은 중간값을 찾는 과정이기 때문에
                        # start_h 는 시작이 255 인 값에서 시작을 해야한다
                        # 오른쪽 끝 픽셀값을 찾는다
                        # 검은색 픽셀을 찾는 후 그 검은색 픽셀의 바깥쪽도 찾는다

                        while True:
                            if m_w + i >= w - 1:
                                right = None
                                break

                            elif cut_img[start_h][m_w + i] == 0:

                                while True:
                                    if m_w + i >= w - 1:
                                        right = None
                                        break

                                    elif cut_img[start_h][m_w + i] == 0:
                                        count += 1
                                        i += 1

                                    else:
                                        if count <= 3:
                                            break

                                        else:
                                            right = m_w + i
                                            break

                                if count <= 4 or right is None:
                                    count = 0
                                    continue

                                else:
                                    break

                            else:
                                i += 1

                        i = 0
                        count = 0
                        # 왼쪽 끝 픽셀값을 찾는다
                        while True:
                            if m_w + i <= 0:
                                left = None
                                break

                            elif cut_img[start_h][m_w + i] == 0:
                                while True:
                                    if m_w + i <= 0:
                                        left = None
                                        break

                                    elif cut_img[start_h][m_w + i] == 0:
                                        count += 1
                                        i -= 1

                                    else:
                                        if count <= 4:
                                            break

                                        else:
                                            left = m_w + i
                                            break

                                if count <= 4 or left is None:
                                    count = 0
                                    continue

                                else:
                                    break

                            else:
                                i -= 1

                        if left is None or right is None:
                            pass

                        else:
                            # 이렇게 middle_w 값을 찾아냈다면
                            # start_h 값을 아까 기억했던 위치로 이동한다 (검은색 픽셀이 발견됬던 곳)
                            middle = round((right + left) / 2)
                            if s == 0 or s == 2:
                                start_h = start_1

                            elif s == 1 or s == 3:
                                start_h = start_2

                            # count 가 6 이상이면 slur 인정
                            count = 0
                            # 아래 반복문의 반복 횟수
                            # 안될 경우가 10번 이상이면 탐색을 중지 후 다음으로 넘어간다
                            re = 0
                            b_distance = None
                            while True:
                                if count >= 3:
                                    is_slur = True
                                    break

                                elif start_h <= 0 or start_h >= h or re >= 10 :
                                    break

                                difference, c_distance, c_left, c_right = \
                                    left_right_difference(cut_img, middle, start_h, w)

                                if difference is None:
                                    if s == 0 or s == 2:
                                        start_h += 1

                                    elif s == 1 or s == 3:
                                        start_h -= 1

                                    continue

                                # 오선줄에 겹치는 경우는 제외한다
                                if c_left <= 0 and c_right >= w - 1:
                                    if s == 0 or s == 2:
                                        start_h += 1

                                    elif s == 1 or s == 3:
                                        start_h -= 1

                                    continue

                                # 처음으로 찾은 값이라면 비교값들을 만든다
                                if b_distance is None:
                                    left = c_left
                                    right = c_right
                                    b_distance = c_distance

                                    if s == 0 or s == 2:
                                        start_h += 1

                                    elif s == 1 or s == 3:
                                        start_h -= 1
                                    continue

                                # 양쪽이 거의 같이 늘어나야 하며 (difference <= 7)
                                # 왼쪽이랑 오른쪽 변화량이 똑같이 증가하는 상황이여야 하며
                                # 이때 왼쪽은 더 적은 값 (더 왼쪽으로 이동) 이 나와야 인정이고
                                # 오른쪽은 더 많은 값 (더 오른쪽으로 이동) 해야 인정이다
                                # 현재 차이가 전 차이 보다 더 커지는 상황이 적어도 6번 (count) 있어야
                                # slur 로 인정한다

                                # 0, 1 방법은 점점 커지는지 확인한다
                                if s <= 1:
                                    if difference <= 7 and b_distance < c_distance and \
                                        c_left < left and c_right > right:
                                        left = c_left
                                        right = c_right
                                        b_distance = c_distance
                                        count += 1
                                        # 찾은 경우이므로 다시 원래대로 되돌린다
                                        re = 0
                                        if s == 0:
                                            start_h += 1

                                        elif s == 1:
                                            start_h -= 1
                                        continue
                                    # 만약 현재 차이가 전 차이 보다 적어지는 경우가 있을 경우
                                    # slur 인정을 안한다
                                    elif b_distance > c_distance:
                                        break

                                    else:
                                        # 더 커진 left, right 값을 비교값으로 바꾼다
                                        if c_left < left:
                                            left = c_left

                                        if c_right > right:
                                            right = c_right

                                        if s == 0:
                                            start_h += 1

                                        elif s == 1:
                                            start_h -= 1

                                        re += 1

                                # 2, 3 방법은 점점 작아지는지 확인
                                elif s >= 2:
                                    if difference <= 7 and b_distance > c_distance and \
                                            c_left > left and c_right < right:
                                        left = c_left
                                        right = c_right
                                        b_distance = c_distance
                                        count += 1
                                        # 찾은 경우이므로 다시 원래대로 되돌린다
                                        re = 0
                                        if s == 2:
                                            start_h += 1

                                        elif s == 3:
                                            start_h -= 1
                                        continue
                                    # 만약 현재 차이가 전 차이 보다 커지는 경우가 있을 경우
                                    # slur 인정 안한다
                                    elif b_distance < c_distance:
                                        break

                                    else:
                                        # 더 작아진 left, right 값을 비교값으로 바꾼다
                                        if c_left > left:
                                            left = c_left

                                        if c_right < right:
                                            right = c_right

                                        if s == 2:
                                            start_h += 1

                                        elif s == 3:
                                            start_h -= 1

                                        re += 1

                    if is_slur is True:
                        break

                    else:
                        start_h = start_2 + 1

            else:
                start_h += 1

    return is_slur

def left_right_difference(cut_img, m_w, h, w):

    i = 0
    # 오른쪽 끝 픽셀값을 찾는다
    # 검은색 픽셀을 찾는 후 그 검은색 픽셀의 바깥쪽도 찾는다
    # 위의 과정은 첫 시작이 255, 0 둘중 뭐든 상관없이 찾을 수 있다
    while True:
        if m_w + i >= w:
            right = None
            break

        if cut_img[h][m_w + i] == 0:

            while True:
                if m_w + i == w:
                    right = None
                    break

                elif cut_img[h][m_w + i] == 0:
                    i += 1
                else:
                    right = m_w + i
                    break
            break

        else:
            i += 1

    i = 0
    # 왼쪽 끝 픽셀값을 찾는다
    while True:
        if m_w + i <= 0:
            left = None
            break

        elif cut_img[h][m_w + i] == 0:

            while True:
                if m_w + i == 0:
                    left = None
                    break

                elif cut_img[h][m_w + i] == 0:
                    i -= 1

                else:
                    left = m_w + i
                    break
            break

        else:
            i -= 1

    if left is None or right is None:
        difference = None
        distance = None

    else:
        left_diff = abs(m_w - left)
        right_diff = abs(m_w - right)

        difference = abs(right_diff - left_diff)
        distance = abs(right - left)


    return difference, distance, left, right


def count_0(w_i, h_i, h, image):

    count = 0
    start = h_i
    end = 0

    while True:
        # h 끝 + 1 에 도달한 경우 w값 올리고 h값 원점으로
        if h_i == h:
            end = h_i - 1
            break

        elif image[h_i][w_i] != 255:
            h_i = h_i + 1
            count = count + 1
            continue

        elif image[h_i][w_i] == 255:
            end = h_i - 1
            break

    return w_i, h_i, count, start, end


def count_0_reverse(w_i, h_i, image):
    count = 0
    start = h_i
    end = h_i + 1

    while True:
        # h 가 -1에 도달한 경우 w값 올리고 h값 원점으로
        if h_i == -1:
            end = h_i + 1
            break
        # 검은 픽셀 일때
        elif image[h_i][w_i] != 255:
            h_i = h_i - 1
            count = count + 1
            continue
        # 흰 픽셀 일때
        elif image[h_i][w_i] == 255:
            end = h_i + 1
            break

    return h_i, w_i, count


def count_255(w_i, h_i, h, image):

    count = 0
    start = h_i
    end = 0

    while True:
        # h 끝 + 1 에 도달한 경우 w값 올리고 h값 원점으로
        if h_i == h:
            end = h_i - 1
            break

        elif image[h_i][w_i] != 0:
            h_i = h_i + 1
            count = count + 1
            continue

        elif image[h_i][w_i] == 0:
            end = h_i - 1
            break

    return w_i, h_i, count, start, end


def count_255_reverse(w_i, h_i, image):
    count = 0
    start = h_i
    end = h_i + 1

    while True:
        # h 가 -1에 도달한 경우 w값 올리고 h값 원점으로
        if h_i == -1:
            end = h_i + 1
            break
        # 흰 픽셀일때
        elif image[h_i][w_i] != 0:
            h_i = h_i - 1
            count = count + 1
            continue
        # 검은 픽셀 일때
        elif image[h_i][w_i] == 0:
            end = h_i + 1
            break

    return h_i, w_i, count


def apply_slur(result, i, i_2, before_octave=[], last_octave=[]):
    """
    슬러를 result 에 적용시킨다.
    그 전 노트와 비교를 한다
    일단 그 전 노트와 현재 노트의 옥타브 리스트를 만듬

    완전 같다면 rest 처리 (change_name = True)
    살짝 다르다면 그 부분만 지운다.

    last_octave 부문은 맨 처음 시작시 slur 가 적용되는
    right_slur_apply = True / left_slur_apply = True 일때
    """
    octave_1 = []  # 현재 노트 (지울 노트)
    octave_2 = []  # 이전 노트 (비교 노트)

    if len(before_octave) >= 1:
        for s in range(0, len(before_octave[0])):
            # 리스트 인지 판단해서 오류 안나게
            if isinstance(before_octave[0][s], list) is True:
                octave_1.append(before_octave[0][s][-1])

            else:
                continue

    elif len(last_octave) >= 1:
        for s in range(0, len(last_octave)):
            octave_1.append(last_octave[s])

    else:
        for s in range(0, len(result[i])):
            # 리스트 인지 판단해서 오류 안나게
            if isinstance(result[i][s], list) is True:
                octave_1.append(result[i][s][-1])

            else:
                continue

    for s in range(0, len(result[i_2])):
        # 리스트 인지 판단해서 오류 안나게
        if isinstance(result[i_2][s], list) is True:
            octave_2.append(result[i_2][s][-1])

        else:
            continue

    is_same = set(tuple(octave_1)) & set(tuple(octave_2))

    if len(is_same) >= len(octave_2):
        result = note_to_rest(result, i_2)

    else:
        del_index = []
        # 지워낼 노트의 옥타브 추출
        for index in range(0, len(is_same)):
            # 비교할 옥타브랑 같은 것이 있다면 지울 리스트에 추가
            for f in range(0, len(octave_2)):
                if octave_1[index] == octave_2[f]:
                    del_index.append(f)
                else:
                    continue

        for delete in range(0, len(del_index)):
            del result[i_2][del_index[delete] - delete]

    return result


def note_to_rest(result, i):
    note_num = result[i][-1]

    if note_num >= 4:
        name = "whole_rest"

    elif note_num >= 2:
        name = "half_rest"

    elif note_num >= 1:
        name = "quarter_4th_rest"

    elif note_num >= 0.5:
        name = "quarter_8th_rest"

    elif note_num >= 0.25:
        name = "quarter_16th_rest"

    elif note_num >= 0.125:
        name = "quarter_32th_rest"

    elif note_num >= 0.0625:
        name = "quarter_64th_rest"

    elif note_num >= 0.03125:
        name = "quarter_128th_rest"

    w = 0
    count = 0
    # 맨 마지막은 note_number 라 뺀다
    for s in range(0, len(result[i]) - 1):
        w += result[i][s][0]
    w = round(w / (len(result[i]) - 1))
    result[i] = [[w, result[i][0][1], name], note_num]

    return result