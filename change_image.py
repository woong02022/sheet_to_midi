import cv2


def preprocess_img(img_path):
    """ 흰, 검이 더 부각된 이미지를 만들고, 높이, 넓이를 계산해 내보낸다."""

    img = cv2.imread(img_path, 0)
    img_draw = cv2.imread(img_path)

    threshold, img = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

    h, w = img.shape
    return h, w, img, img_draw


def find_diff_w(img, staff_lines):
    # w 시작 값을 찿는다
    w = find_start_bar_line(img, staff_lines) + 10  # +10은 bar 랑 계산이 겹치지 않기 위해서

    start_h = staff_lines[0]
    end_h = staff_lines[4]

    # start_point clef 의 시작 w 값을 찾는다
    while True:
        if img[start_h][w] == 0:
            # 오선줄에 겹치는 검은색 픽셀값을 찾은 것이 아니라면
            # clef 의 첫 시작점을 찾은 것이므로
            if not (start_h == staff_lines[0] or
                    start_h == staff_lines[1] or
                    start_h == staff_lines[2] or
                    start_h == staff_lines[3] or
                    start_h == end_h):
                start_point = w
                break

            elif start_h == end_h:
                start_h = staff_lines[0]
                w += 1

            else:
                # 검은색 픽셀을 다 지나치고 나서 재 검색
                while True:
                    start_h += 1
                    if img[start_h][w] == 255:
                        break
                    else:
                        continue
        else:
            start_h += 1

    while True:
        if img[start_h][w] == 0:
            # 오선줄에 겹치는 검은색 픽셀값을 찾은 것이 아니라면
            # clef 의 첫 시작점을 찾은 것이므로
            if not (start_h == staff_lines[0] or
                    start_h == staff_lines[1] or
                    start_h == staff_lines[2] or
                    start_h == staff_lines[3] or
                    start_h == end_h):
                w += 1
                start_h = staff_lines[0]

            elif start_h == end_h:
                end_point = w
                break

            else:
                # 검은색 픽셀을 다 지나치고 나서 재 검색
                count = 0
                while True:
                    start_h += 1
                    count += 1
                    if img[start_h][w] == 255:
                        break
                    elif count >= 10:
                        break
                    else:
                        continue
        else:
            start_h += 1
    diff_w = end_point - start_point

    return diff_w


def find_start_bar_line(image, staff_lines):

    w = 0  # 0 부터 검색

    end_h, end_w = image.shape

    start = staff_lines[0]  # 높은 음자리표 오선 중 맨 윗 부분
    end = staff_lines[9]  # 낮은 음자리표 오선 중 맨 아랫 부분

    middle = (start + end) // 2  # 그 사이에 0 픽셀이 존재 한다면 그 부분은 bar 예상 지점이다.

    while True:
        # 끝에 도달한 경우
        if end_w == w:
            break
        # 가운데 쪽 검은색 픽셀이 발견된다면 >> bar 탐지 시작
        if image[middle][w] == 0:
            # 해당 라인에 bar가 감지 되는 지 확인
            t_f = count_0_for_bar(image, middle, start, end, w)

            if t_f is True:
                break

        w += 1
    return w


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
        if start_h >= middle - i:
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
            if end_h <= middle + i:
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


def resize_img(h, w):
    # 크기 규격 설정
    set_h = 104
    set_w = 72

    diff_h = set_h - h
    diff_w = set_w - w

    if diff_w == 0 and diff_h == 0:
        is_same = True
    else:
        is_same = False

    change_h = diff_h * 20
    change_w = diff_w * 45

    return change_h, change_w, is_same
