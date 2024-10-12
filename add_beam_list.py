import copy

beam_list = [
    '4th',
    '8th',
    '16th',
    '32th',
    '64th',
    '128th'
]


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

    return w_i, h_i, count, start, end


def make_dot_and_beam(result, image, h, staff_interval):
    """
    여기서 제일 빠른 노트를 선정해 그 노트가 dot 가 있으면 dot 정보까지 넣는게 맞지 않을까
    """
    n_dic = {
        '1th': 4,
        '2th': 2,
        '4th': 1,
        '8th': 0.5,
        '16th': 0.25,
        '32th': 0.125,
        '64th': 0.0625,
        '128th': 0.03125
    }

    note_num = 0
    # 제일 작은 값이 모아진 노트 리스트의 속도가 된다

    lower_i = 0
    for r in range(0, len(result)):
        lower_num = 4
        for s in range(0, len(result[r])):
            if result[r][s][2].find('quarter') >= 0:
                if result[r][s][2].find('note') >= 0:
                    beam_count = beam(result, image, h, r, s)

                    note_name = beam_list[beam_count]
                    note_num = n_dic[note_name]

                elif result[r][s][2].find('rest') >= 0:
                    if result[r][s][2].find('4th') >= 0:
                        note_name = '4th'
                        note_num = n_dic[note_name]

                    elif result[r][s][2].find('8th') >= 0:
                        note_name = '8th'
                        note_num = n_dic[note_name]

                    elif result[r][s][2].find('16th') >= 0:
                        note_name = '16th'
                        note_num = n_dic[note_name]

                    elif result[r][s][2].find('32th') >= 0:
                        note_name = '32th'
                        note_num = n_dic[note_name]

            elif result[r][s][2].find('half') >= 0:
                note_name = '2th'
                note_num = n_dic[note_name]

            elif result[r][s][2].find('whole') >= 0:
                note_name = '1th'
                note_num = n_dic[note_name]

            else:
                note_num = -1
                continue

            if note_num < lower_num:
                lower_num = note_num
                lower_i = s

        if note_num <= 0:
            continue
        # 제일 낮은 값의 num 을 얻었으니
        # 이 노트에 dot 를 적용해야 하는지 아닌지 판단
        # 일단 제일 낮은 note_name 을 얻는다
        # note_name = get_key(lower_num, n_dic)
        dot_i = find_near_right_dot(result, r)

        while True:
            if dot_i == 'none':
                break

            is_dot = accept_dot(result, staff_interval, dot_i, r, lower_i)

            if is_dot == 'true':
                # note_name += '_dot'
                lower_num = lower_num * 1.5
                break

            # 노트, dot 와의
            # w 차이가 75 이하인 경우
            elif is_dot == 'next':
                dot_i = find_near_right_dot(result, dot_i)

            # 75 이상인 경우
            elif is_dot == 'false':
                break

        result[r].append(lower_num)

    return result


def get_key(val, my_dict):
    for key, value in my_dict.items():
        if val == value:
            return key

    return "none"


def find_near_right_dot(result, i):
    """

    오른쪽 근처에 있는 dot 을 찿는다.

    """
    while True:
        i += 1

        if i >= len(result):
            i = 'none'
            break

        if result[i][0][2].find('dot') >= 0:
            break

    return i


def accept_dot(result, staff_interval, dot_i, r, lower_i):
    """


    # 점?분음표 라면

        h 차이 >> +- staff_interval

        w 차이 (절댓값 x : 노트 헤드는 점 기준 왼쪽 위치)>> 75 (80까지도 봐야 할듯) 이하

    # 스타카토 라면

        아래, 위 위치 파악 먼저 (차이 계산 법이 달라짐)

        h 차이 >> +- (staff_interval + 15)

        w 차이 >> 15 내외

    """

    dot_accept = 'false'

    dot_w = result[dot_i][0][0]
    dot_h = result[dot_i][0][1]
    # left_i 존재 한다면

    note_w = result[r][lower_i][0]
    note_h = result[r][lower_i][1]

    w_diff = dot_w - note_w
    h_diff = abs(dot_h - note_h)

    # w 차이 10(너무 가까우면 스타카토) ~ 75 이내 / h 차이 스태프 사이 거리 이내
    # 적용이 완료 됬다면 스타카토 적용이 되면 안되므로
    # continue 로 다음 회차로 넘어간다.
    if 10 <= w_diff <= 50 and h_diff <= staff_interval:
        dot_accept = 'true'

    elif 10 <= w_diff <= 50:
        dot_accept = 'next'

    return dot_accept


def up_or_down(compare, up, down):
    """
    노트헤드의 h 중간값, 스템 h 맨 위 값, 스템 h 맨 아랫 값

    스템 h 아랫값과 노트헤드의 중간값의 차이가 15이하 라면
    스템은 위쪽을 향해져 있을것이다 (아래와 차이가 별로 없으므로 )
    반대로 15 이상이면 노트 헤드 중간으로부터 아래로 길다는 것

    """
    if abs(compare - down) <= 15:
        return up, 'up'

    elif abs(compare - up) <= 15:
        return down, 'down'

    else:
        return 0, 'none'


def find_different_stem(result, r):
    """
    겹쳐있는 quarter_note 중 다른 스템값이 있으면 서로 4th, 8th 이런
    박자가 다른 경우가 있으므로 이것을 방지하기 위해
    다른 스템값이 있는 인덱스 리스트를 만든다.

    compare_i = [] : 여기엔 다른 스템값이 모여있는 i 값이며
    나중에 새로운 스템값이 들어왔는지 똑같은게 들어왔는지 비교하는 인덱스 로도 사용


    """
    compare_i = []
    for i in range(0, len(result[r])):
        # 처음에는 비교할 것도 없으므로 비교 인덱스 리스트에 넣는다
        if i == 0:
            compare_i.append(i)

        else:
            # 일단 아래 있는 compare_i 를 다 돌아야
            # 같은 스템인지 아닌지 판단이 가능 하므로 아래 반복을 다 돌려도
            # 같은 스템이 없으면 same 은 False 그대로 간다
            # 만약 같은게 있다면 바로 반복을 중지 후 same = True 로 바꾼다

            same = False
            # compare_i 리스트에 있는 인덱스 저장값을 현재 값이랑 전부 비교한다.
            for s in range(0, len(compare_i)):
                # result[r][비교할 인덱스 값]
                compare_index = compare_i[s]

                # 비교 스템 h 위 값
                compare_h_1 = result[r][compare_index][3]
                # 비교 스템 h 아래 값
                compare_h_2 = result[r][compare_index][4]
                # 비교 스템 w 값
                compare_w = result[r][compare_index][5]

                # 현재 값들
                current_h_1 = result[r][i][3]
                current_h_2 = result[r][i][4]
                current_w = result[r][i][5]

                diff_h_1 = abs(compare_h_1 - current_h_1)
                diff_h_2 = abs(compare_h_2 - current_h_2)
                diff_w = abs(compare_w - current_w)

                # 똑같은 스템값으로 인정
                if diff_h_1 <= 10 and diff_h_2 <= 10 and diff_w <= 10:
                    same = True
                    break

            # 같은 스템이 없으므로 새로운 스템 인덱스 i 값으로 추가
            if same is False:
                compare_i.append(i)

    return compare_i


def beam(result, image, h, r, index):

    """

    up = -

    down = reverse

    """
    # 스템 w 값
    w_i = result[r][index][5]
    # (노트헤드 중간값, 스템 맨 위, 아랫 값) 의 정보로 어느 방향이
    # 꼬리 인지 판단 후 h 값을 판단.
    h_i, up_down =\
        up_or_down(result[r][index][1], result[r][index][3], result[r][index][4])
    # (노트헤드의 h 중간값, 스템 h 맨 위 값, 스템 h 맨 아랫 값)

    # 스템의 중간에 낀 노트이므로 이 노트는 빔을 구분 못하므로 4th 로 리턴값을 낸다
    if up_down == 'none':
        return 0

    # image, left_down_w_i, left_down_h_i, h, 'left', 'down'
    right_beam_count = 0
    left_beam_count = 0

    for i in range(1, 7):

        left_beam_count = find_beam(image, w_i - i, h_i, h, up_down)

        if left_beam_count == 0:
            continue

        else:
            break

    for i in range(1, 7):
        right_beam_count = find_beam(image, w_i + i, h_i, h, up_down)

        if right_beam_count == 0:
            continue

        else:
            break

    if left_beam_count >= right_beam_count:
        current_beam_count = left_beam_count

    else:
        current_beam_count = right_beam_count

    return current_beam_count


def find_beam(image, w_i, h_i, h, up_or_down):

    beam_count = 0

    skip = 0

    # 그전부터 건들어야 한다. 아까 만든 w 값으로 0 ~ 6 번째 까지
    if up_or_down == 'up':

        for i in range(0, 20):

            if skip >= 1:
                skip = skip - 1
                continue

            elif image[h_i + (i - 4)][w_i] == 255:
                continue

            elif image[h_i + (i - 4)][w_i] == 0:
                a, h_i, count, c, d = count_0(w_i, h_i + (i - 4), h, image)

                # 예상 빔 값 안에 들어왔다면
                if 9 <= count <= 26:
                    # 8분음표, 16분음표 등 어떤 종류의 빔인지 파악
                    beam_count = count_beam(image, w_i, h_i + (i - 4), h)
                    break

                # 검은 픽셀이 3이하로 발견된다면 (스킵)
                elif count <= 3:
                    skip = count  # count 수만큼 검은픽셀을 스킵한다.
                    continue

                else:
                    beam_count = 0
                    break

    elif up_or_down == 'down':

        for i in range(0, 20):

            if skip >= 1:
                skip = skip - 1
                continue

            elif image[h_i - (i - 4)][w_i] == 255:
                continue

            elif image[h_i - (i - 4)][w_i] == 0:
                a, h_i, count, c, d = count_0_reverse(w_i, h_i - (i - 4), image)

                if 11 <= count <= 26:
                    beam_count = count_beam_reverse(image, w_i, h_i)

                    break

                elif count <= 3:
                    skip = count
                    continue

                else:
                    beam_count = 0
                    break

    return beam_count


def count_beam(image, w_i, h_i, h):

    beam_count = 1

    m = 1

    while True:

        if m >= 9:
            break

        elif image[h_i + m][w_i] == 255:
            m = m + 1
            continue

        elif image[h_i + m][w_i] == 0:
            origin_h = copy.deepcopy(h_i)
            a, h_i, count, c, d = count_0(w_i, h_i + m, h, image)

            if 11 <= count <= 26:
                beam_count = beam_count + 1
                m = 1
                continue

            elif count <= 3:
                h_i = origin_h
                m += count
                continue

    return beam_count


def count_beam_reverse(image, w_i, h_i):

    beam_count = 1

    m = 1  # 빔과 빔의 간격차이
    while True:

        # m > 빔과 빔의 간격차이를 적는곳
        if m >= 9:
            break

        elif image[h_i - m][w_i] == 255:
            m = m + 1
            continue

        elif image[h_i - m][w_i] == 0:
            origin_h = copy.deepcopy(h_i)
            a, h_i, count, c, d = count_0_reverse(w_i, h_i - m, image)

            if 11 <= count <= 26:
                beam_count = beam_count + 1
                m = 1
                continue

            elif count <= 3:
                h_i = origin_h
                m += count
                continue

    return beam_count