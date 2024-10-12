from classifier import *

time_list = {
    'two_two_time': 4,  # 한 마디 당 2분음표가 2개 == 4분음표가 4개
    'four_four_time': 4,  # 한 마디 당 4분음표가 4개
    'four_three_time': 3  # 한 마디 당 4분음표가 3개
}


def count_0_for_bar(image, middle, start_h, end_h, w):
    """
    bar 의 탐지를 위해 0 (검은색 픽셀) 을 찿는다.

    두 오선 사이에 중간지점 에 검은색 픽셀을 찿았다면 여기로 오므로
    그 중간 지점 기준 위, 아래로 길게 뻗어있는 구조라면 bar라고 인식을 한다.
    """
    i = 0

    # 위부터 확인

    while True:
        # start 지점 (높은 음자리표 오선줄 맨 위) 보다 높다면
        # 위쪽은 bar 기준에 해당하므로 up = True 표시를 한다.
        if start_h + 5 >= middle - i >= start_h - 5:
            up = True
            break
        # 계속 검은색 픽셀이 있는지 확인 한다.
        elif image[middle - i][w] == 0:
            i += 1
        # 중간에 검은색 픽셀이 끊겼다면 bar 기준에 해당 x
        else:
            up = False
            break
    # 위가 확정이 난 경우에만 down 을 탐색한다. (계산을 줄이기 위해)
    if up is True:
        i = 0
        while True:
            if end_h + 5 >= middle + i >= end_h - 5:
                down = True
                break

            elif image[middle + i][w] == 0:
                i += 1

            else:
                down = False
                break

        if down is True:
            return True

        else:
            return False

    else:
        return False


def get_staff_lines(w, height, in_img):

    # 스태프 추측값 = 전체 가로 70%
    staff_presume = round(w * 0.7)
    # 가로의 중간값
    half_w = round(w / 2)

    staff_lines = []

    for h in range(0, height):
        if in_img[h][half_w] == 0:

            left_i = 1
            right_i = 1

            left = 0
            right = 0

            # left 의 숫자를 알아냄
            while True:
                try:
                    if in_img[h][half_w - left_i] == 0:
                        left += 1
                        left_i += 1

                    else:
                        break
                except IndexError:
                    break

            # right 의 숫자를 알아냄
            while True:
                try:
                    if in_img[h][half_w + right_i] == 0:
                        right += 1
                        right_i += 1

                    else:
                        break
                except IndexError:
                    break

            if left + right >= staff_presume:
                staff_lines.append(h)

            else:
                continue
        else:
            continue

    staff_lines = start_staff_line(staff_lines)

    # staff_lines = find_real_staff_line(staff_lines)

    return staff_lines


def start_staff_line(staff_line):
    before = staff_line[0]

    new_staff_line = [staff_line[0]]

    for i in range(1, len(staff_line)):

        if staff_line[i] - before > 1:
            new_staff_line.append(staff_line[i])
            before = staff_line[i]

        else:
            before = staff_line[i]
            continue

    return new_staff_line


def find_bar_lines(image, staff_lines, end_w, symbol_list):
    i = 0  # 높은 음자리표 오선줄 중 맨윗값
    i_2 = 9  # 낮은 음자리표 오선줄 중 맨아랫값

    w = 0  # 0 부터 검색

    current_w = 0  # 현재 계산중인 bar w 값
    before_w = 100  # 그 전에 나온 bar w 값 (겹세로줄 판별을 위해)

    bar_second = 0

    for s in range(0, len(staff_lines) // 10):
        start = staff_lines[i]  # 높은 음자리표 오선 중 맨 윗 부분
        end = staff_lines[i_2]  # 낮은 음자리표 오선 중 맨 아랫 부분

        middle = (start + end) // 2  # 그 사이에 0 픽셀이 존재 한다면 그 부분은 bar 예상 지점이다.

        count = 0
        while True:
            # 끝에 도달한 경우
            if end_w == w:
                break
            # 가운데 쪽 검은색 픽셀이 발견된다면 >> bar 탐지 시작
            if image[middle][w] == 0:
                # 해당 라인에 bar가 감지 되는 지 확인
                t_f = count_0_for_bar(image, middle, start, end, w)

                if t_f is True:
                    count += 1  # bar 의 굵기 때문에 여러번 인식될 수 있으므로 count 를 세준다

                w += 1

            # 가운데 쪽 흰 픽셀이라면 >> bar 탐지가 끝났거나, 넘어가야할 구간
            else:
                # count(예상 bar 의 h 가 값) 상으로 길이 1 ~ 6 일때 bar 최종 결정이 된다.
                if 1 <= count <= 6:
                    current_w = w

                    # 겹세로줄 판단 여부 (bar 의 앞 뒤 차이 15 이하 라면 겹세로줄)
                    if abs(current_w - before_w) <= 15:
                        # 높은, 낮은 음자리표 쪽 가운데 스태프 위치 좌표에 각각
                        # double_bar 를 넣는다.
                        symbol_list.append((current_w, staff_lines[i + 2], 'double_bar'))
                        symbol_list.append((current_w, staff_lines[i_2 - 2], 'double_bar'))

                    # 겹세로줄이 아니므로 bar를 넣는다
                    else:
                        symbol_list.append((current_w, staff_lines[i + 2], 'bar'))
                        symbol_list.append((current_w, staff_lines[i_2 - 2], 'bar'))
                    before_w = current_w

                # 0 (검은색) 이 연속으로 발견되어야 bar 길이를 특정할 수 있으므로
                # 255 (흰색) 구간은 아래 구문을 실행한다
                count = 0
                w += 1

        i += 10  # 다음 높은음자리표의 스태프로 이동
        i_2 += 10  # 다음 낮은음자리표의 스태프로 이동
        w = 0
    # current_w 는 end_line 이 된다 (맨 마지막에 계산된 bar 이므로
    return bar_second, symbol_list


def find_real_staff_line(staff_lines):
    count = 0
    i = 0

    while True:

        if i >= len(staff_lines) - 1:
            break

        elif count <= 3:
            if 20 <= staff_lines[i + 1] - staff_lines[i] <= 30:
                count += 1
                i += 1

            else:
                del staff_lines[i]

        elif count == 4:
            if 80 <= staff_lines[i + 1] - staff_lines[i]:
                count = 0
                i += 1

            else:
                del staff_lines[i + 1]

        elif count >= 5:
            count = 0

    return staff_lines