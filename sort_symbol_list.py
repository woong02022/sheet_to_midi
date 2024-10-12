from add_beam_list import *
from difflib import SequenceMatcher


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


def sort_list(height_start, height_end, tuple_list):
    """
    한 스태프(오선줄)의 높이 최소값, 최대값을 얻어서 그중 감지된 좌표를
    리스트에서 따로 빼서 구분한다.

    그 전 오선줄 + a == 높이 최소값

    다음 오선줄 + a == 높이 최대값
    """
    new_sort = []
    for i in range(0, len(tuple_list)):
        # 범위 내에 h(높이) 값이 들어올 경우
        if height_start < tuple_list[i][1] < height_end:
            new_sort.append(copy.deepcopy(tuple_list[i]))

        else:
            continue

    return new_sort


def make_stem(sort_new, image, h):
    """
    note, blank 값에 stem_top_h, stem_end_h, stem_w 값의 정보를 구해서
    sort_new 에 넣는다.
    """
    for i in range(0, len(sort_new)):
        if sort_new[i][2].find('note') >= 0:
            sort_new = stem_find_and_in(sort_new, image, h, i, 'note')

        else:
            continue

    return sort_new


def stem_find_and_in(result, image, h, r, n_b):
    """

    result[0] = w
    result[1] = h
    result[2] = '이름'

    결과값 (노트에 추가되는 값) : top, end, w_i
        """
    # n_b : note / blank
    if n_b == 'note':
        start = 13

    elif n_b == 'blank':
        start = 5

    # 왼쪽
    for i in range(start, 23):
        left = result[r][0] - i  # 왼쪽으로 이동하는 w_i 값

        left_up_w_i, left_up_h_i, left_up, left_up_start, left_up_end = \
            count_0_reverse(left, result[r][1] - 10, image)
        left_down_w_i, left_down_h_i, left_down, left_down_start, left_down_end = \
            count_0(left, result[r][1] + 10, h, image)

        if left_up >= 45:

            top = left_up_end
            # a b c d 는 아래쪽에서 역할이 없는 변수들이다
            a, b, c, d, end = count_0(left_up_w_i, left_up_end, h, image)

            add = (top, end, left_up_w_i)

            result[r] += add

            break

            # 이렇게 w_i 가 같으며 top end 차이가 3 혹은 4이상 안차이 나는 것들만 모아서 뭉치면
            # 더 효과적으로 판별하능 할듯 빔 찿는건 모인 다음 나중에 따로 값 넣어서 하면 될듯

            # beam_count_left = beam(image, left_up_w_i, left_up_h_i, h, 'left', 'up')

        elif left_down >= 45:

            end = left_down_end

            a, b, c, d, top = count_0_reverse(left_down_w_i, left_down_end, image)

            add = (top, end, left_down_w_i)

            result[r] += add

            break

    # 오른쪽
    for i in range(start, 23):

        right = result[r][0] + i  # 오른쪽으로 이동하는 w_i 값

        right_up_w_i, right_up_h_i, right_up, right_up_start, right_up_end = \
            count_0_reverse(right, result[r][1] - 10, image)
        right_down_w_i, right_down_h_i, right_down, right_down_start, right_down_end = \
            count_0(right, result[r][1] + 10, h, image)

        if right_up >= 45:
            top = right_up_end

            a, b, c, d, end = count_0(right_up_w_i, right_up_end, h, image)

            add = (top, end, right_up_w_i)

            result[r] += add

            break

        elif right_down >= 45:
            end = right_down_end

            a, b, c, d, top = count_0_reverse(right_down_w_i, right_down_end, image)

            add = (top, end, right_down_w_i)

            result[r] += add

            break

    try:
        exist = result[r][3]

    except IndexError:
        add = (0, 0, 0)

        result[r] += add

    return result


def sort_w_list(sort_new, staff_up, staff_down,
                image, staff_interval, img_h, staff_over_up, staff_over_down):
    """
    노트와 심볼 결합을 한다.

    노트는 /좌표 정보/스템유무/현재 여기 스태프에 들어와도 되는지/ 등 여러가지 정보를
    보고 넣을지 그리고 합칠지를 판단한다.
    (whole_note 는 3번방법으로 스태프 들어오는지 체크만 하고 w, h 5이하 인지에 따라 합친다)

    심볼같은 경우는 sort_new 바로 /다음 인덱스/w,h 차이 5 이하/이름이 같은지
    이 3가지 경우로 합친다.

    1. w 차이가 35 이내이고 스템이 오선줄 안에 들어오는지
    ( 오선줄 안 노트인지 확인 하는 과정 )

    2. 1번이 안될 때 노트 중 오선줄 (범위 +- 2.25x)안에 들어오는 것이 있는지 확인한다.

    3. 2번이 안될때 오선줄에 제일 가까운
    노트중 blank 가 있다고 가정하고
    흰 픽셀 컬러를 세면서 스태프 거리
    이상으로 많을 시 해당 노트에 안들어 온다고
    판단 후 제외 시킨다. (오류가 있을 수 있음)

    4. 스템값이 0가 아닐 경우 (존재할 경우) 스템값이 위 혹은 아래 오선줄 에 닿지 않는지 확인
    -------------------------------
    스템값이 없는 것은

    일단 보류 후 그 노트 자체가

    오선줄 안에 들어 갈 수 있는 노트인지

    3번 방법으로 판단만 한다.

    그리고 나중에 w 35 이내 차이 라면 서로 합치는 방식으로 간다.
    (나중에 35 이내 차이 중 스템으로 합쳐진 두 노트 중 하나는 35 이내가 아닐 수 도 있는 경우가
    있을 수 있는데 35 차이 이내가 있는 노트가 1개라도 있으면 합치는 구조로 간다)
    --------------------------------------
    합치는 기준
    1. 노트헤드 w 차이 35 내 (아니라면 콤바인(결합) 리스트에서 제거 후 처리)
    2. 스템값 비슷하고
    3. 이름 같고 (quarter, half, whole...)
    4. 마지막으로 t_or_f (이 오선줄에 들어가는 노트가 맞는지에 대한 판단 여부) 수정여부

    combine_list = [w값, i값 (result 내, t_or_f)]
    이 리스트로 정보를 비교해가며 계속 합칠 수 있게 만든다.

    """
    global i_2

    # combine_list = [w값, i값, 이름, true/false] # 비교를 위해 만들어짐
    combine_list = []

    # symbol 용
    combine_list_2 = []
    # 새로운 리스트
    new_list = []

    # 나중에 new_list 에서 지울 i 값 모으는 용도
    del_list = []

    # stem 이 없는 blank 의 리스트
    no_stem = []

    i = 0
    while True:

        i += 1

        if i >= len(sort_new):
            break

        if sort_new[i][2].find('note') > -1:

            # 합치고 있는 노트가 있다면 >>
            if len(combine_list) >= 1:

                """
                combine_list 에 있는 것들중 w 값이 현재 계산하고 있는 것과
                36 이상 차이가 난다면 이미 더 합칠 것이 없는 것이므로 
                리스트에서 지운다.
                
                단 지우기 전에 오선줄에 확실히 들어갈 수 
                있는지의 여부를 봐야 하므로 inside_staff_1, 2, 3 과정으로 
                들어갈 수 있는지에 대한 여부를 확인 후 최종 판단 후 지울 거면 
                지우고 남길거면 남기는 선택을 해야 한다. 
                """
                current_w = sort_new[i][0]
                n = 0  # combine_list 순환 반복자
                while True:
                    if n == len(combine_list):
                        break
                    # 현재 노트 차이가 41 이상, 스템 w 값 차이가 10 이상 나는 경우
                    # 현재 combine 리스트에 있는 노트는 더 합칠게 없다고 판단 후
                    # 마지막으로 정말 들어올 수 있는 노트인지 판단 후 combin 리스트에서 제거

                    elif abs(current_w - combine_list[n][0]) >= 41 and \
                        abs(new_list[compare_i][0][5] - sort_new[i][5]) > 10:
                        combine_list, del_list = inside_staff_all(staff_up, staff_down,
                                        new_list, del_list, combine_list, n, image,
                                        staff_interval, img_h, staff_over_up, staff_over_down)
                        if n == 0:
                            continue

                        n -= 1

                    else:
                        n += 1

                # 스템 값이 있는 경우 , 혹은 온음표 인 경우 (무조건 스템 x)

                if not sort_new[i][3] == 0 and not sort_new[i][4] == 0 or not\
                    sort_new[i][2].find('whole') >= 0:
                    n = 0  # combine_list 순환 반복자
                    # combine_list 순환하면서 w 차이 35 이내 이면서
                    # 스템값이 맞는것이 있는지 찿는다.
                    while True:
                        # combine_list 를 다 돌아봐도 같은 스템값이 없을 시
                        # 새로운 노트를 combine_list 에 추가한다.
                        # 오선줄에 확실히 들어갈 수 있는지의 여부를 봐야 하므로
                        # inside_staff_3 과정으로 검사를 한다
                        if n >= len(combine_list):
                            w = sort_new[i][0]
                            h = sort_new[i][1]

                            t_or_f = inside_staff_3(w, h, image, staff_interval,
                                                    staff_up, staff_down, img_h)
                            # 3번 과정이 통과된다면 4번으로도 확인 후 통과 된다면
                            # combine_list 에 넣는다
                            if t_or_f is True:
                                stem_up_h = sort_new[i][3]
                                stem_down_h = sort_new[i][4]
                                t_or_f = inside_staff_4\
                                    (staff_over_up, staff_over_down, stem_up_h, stem_down_h)

                                if t_or_f is True:
                                    new_list, combine_list = \
                                        combine_list_in(staff_up, staff_down,
                                                        sort_new, new_list, combine_list, i)

                                # 만약 스템값이 현재 자신의 오선줄과 다음 오선줄 만 침범하는 경우 라면
                                # 위, 현재 (같이 겹침) / 아래, 현재 (같이 겹침)
                                elif (stem_up_h < staff_over_up and \
                                        staff_over_down > stem_down_h and \
                                        staff_up < stem_down_h) or \
                                        (stem_up_h > staff_over_up and \
                                        staff_over_down < stem_down_h and \
                                        staff_down > stem_up_h):

                                   # 현재 노트가 현재 오선줄의 over_up 부터 staff_down 까지 이다
                                   if staff_over_up <= sort_new[i][1] <= staff_down:
                                            new_list, combine_list = \
                                                combine_list_in(staff_up, staff_down,
                                                                sort_new, new_list, combine_list, i)

                            break

                        compare_i = combine_list[n][1]


                        # 스템 값이 서로 같은 경우 (차이가 10 이하 면 같은걸로 간주)
                        # new_list 에 있는 해당 인덱스 노트에 추가 한다.
                        # 23.02.17 abs(new_list[compare_i][0][0] - sort_new[i][0]) <= 40
                        # 노트 w로 비교하지 않고 스템 w 로 비교를 한다
                        # >> abs(new_list[compare_i][0][5] - sort_new[i][5]) <= 10
                        if abs(new_list[compare_i][0][5] - sort_new[i][5]) <= 10 and \
                            abs(new_list[compare_i][0][3] - sort_new[i][3]) <= 10 and \
                            abs(new_list[compare_i][0][4] - sort_new[i][4]) <= 10:
                            t_or_f = inside_staff_4 \
                                (staff_over_up, staff_over_down, stem_up_h, stem_down_h)

                            if t_or_f is True:
                                new_list[compare_i].append(list(sort_new[i]))

                            elif (stem_up_h < staff_over_up and \
                                        staff_over_down > stem_down_h and \
                                        staff_up < stem_down_h) or \
                                        (stem_up_h > staff_over_up and \
                                        staff_over_down < stem_down_h and \
                                        staff_down > stem_up_h):

                                # 현재 노트가 현재 오선줄의 over_up 부터 staff_down 까지 이다
                                if staff_over_up <= sort_new[i][1] <= staff_down:
                                    new_list[compare_i].append(list(sort_new[i]))

                            break

                        # (23.02.19) 노트헤드 w 차이가 15 이내 라면
                        # 15 이내 라도 이 노트가 해당 오선줄에 넣을 수 있는지 판단을 해야 하므로
                        # 세번째 (blank 검사) 방법을 써서 True 라면 넣는다
                        elif abs(new_list[compare_i][0][0] - sort_new[i][0]) <= 10:
                            w = sort_new[i][0]
                            h = sort_new[i][1]
                            t_or_f = inside_staff_3(w, h, image, staff_interval,
                                                    staff_up, staff_down, img_h)

                            if t_or_f is True:
                                new_list[compare_i].append(list(sort_new[i]))
                                break

                        # 둘다 해당되지 않는다면 다음 combine_list 에 있는 값을 비교
                        n += 1

                # 스템 값이 없는 경우 (whole 노트)
                # quarter, half 는 스템값이 없을리 없으므로 합치지 않는다
                else:
                    if sort_new[i][2].find('whole') >= 0:
                        w = sort_new[i][0]
                        h = sort_new[i][1]
                        t_or_f = inside_staff_3(w, h, image, staff_interval,
                                                staff_up, staff_down, img_h)

                        if t_or_f is True:
                            new_list.append([list(sort_new[i])])
                            current_index = len(new_list) - 1

            else:
                # 노트 첫 추가
                # ex) new_list[0] ==
                # [[(773(0), 1428(1), 'quarter_note_head_4'(2),1425(3), 1560(4), 758(5))]]
                # [노트헤드 w값(0), 노트헤드 h값(1), 이름(2), 스템 위 h값(3), 스템 아래 h값(4), 스템 w값(5)]
                # combine_list = [비교할 w 값(0), new_list 인덱스 값(1), 이름(2), t_or_f(3)]
                # true / false (이 오선줄에 들어가는 노트가 맞는지에 대한 판단 여부)
                # combine_list 에 새 노트 추가 후 나중에 검사할 노트 중 같이 합쳐지는지 확인

                w = sort_new[i][0]
                h = sort_new[i][1]
                t_or_f = inside_staff_3(w, h, image, staff_interval,
                                        staff_up, staff_down, img_h)
                # 추가 전 3번 방법으로 스태프에 들어와도 되는 노트인지 판별한다
                if t_or_f is True:
                    # 또한 4번 방법까지 통과가 된다면

                    stem_up_h = sort_new[i][3]
                    stem_down_h = sort_new[i][4]

                    # 스템값이 존재하지 않는 경우
                    if stem_up_h == 0 and stem_down_h == 0:
                        t_or_f = True

                    else:
                        t_or_f = inside_staff_4 \
                            (staff_over_up, staff_over_down, stem_up_h, stem_down_h)

                    if t_or_f is True:
                        new_list, combine_list = \
                            combine_list_in(staff_up, staff_down,
                                            sort_new, new_list, combine_list, i)

                        compare_i = combine_list[0][1]

                    # 만약 스템값이 현재 자신의 오선줄과 다음 오선줄 만 침범하는 경우 라면
                    # 위, 현재 / 아래, 현재
                    elif (stem_up_h < staff_over_up and \
                            staff_over_down > stem_down_h and \
                            staff_up < stem_down_h) or \
                            (stem_up_h > staff_over_up and \
                            staff_over_down < stem_down_h and \
                            staff_down > stem_up_h):

                        # 현재 노트가 현재 오선줄의 over_up 부터 staff_down 까지 이다
                        if staff_over_up <= sort_new[i][1] <= staff_down:
                            new_list, combine_list = \
                                combine_list_in(staff_up, staff_down,
                                                sort_new, new_list, combine_list, i)

                            compare_i = combine_list[0][1]


        # 노트가 아니라도 겹쳐진 여러개의 좌표들이 있을 수 있으니
        # 다음과 같이 w, h 차이가 5 이하 이거나
        else:
            new_list.append([list(sort_new[i])])
            current_index = len(new_list) - 1
            while True:
                try:
                    w_diff = abs(sort_new[i][0] - sort_new[i + 1][0])
                    h_diff = abs(sort_new[i][1] - sort_new[i + 1][1])
                    # "sharp_2" 라고 한다면 "sharp" 로 바꿔서 같은 이름인지 확인한다
                    is_same = sort_new[i][2][:-2] == sort_new[i + 1][2][:-2]
                except IndexError:
                    break

                if w_diff <= 5 and h_diff <= 5 and is_same is True:
                    new_list[current_index].append(list(sort_new[i + 1]))
                    i += 1
                else:
                    break


    # 마지막으로 combine_list 에 계산을 못한 노트가 있을 수 있으니
    # 검사 후 마무리
    n = 0  # combine_list 순환 반복자
    while True:
        if n >= len(combine_list):
            break

        combine_list, del_list = inside_staff_all\
            (staff_up, staff_down, new_list, del_list, combine_list, n, image,
                staff_interval, img_h, staff_over_up, staff_over_down)

    return new_list, del_list


def combine_list_in(staff_start, staff_end, sort_new,
            new_list, combine_list, i):
    """
    # combine_list = [비교할 w 값(0), new_list 인덱스 값(1), 이름(2)]

    현재 검사할려는 노트 값이 해당 start, end 값 사이에 있는
    값인지 검사 후 현재 오선줄에 해당 되는 값이면
    true 아니면 false 로 판단 후 내보낸다

    스템값 0, 0는 거른다. """

    new_list.append([list(sort_new[i])])
    combine_i = len(new_list) - 1  # new_list 에 해당되는 인덱스 값
    combine_list.append([sort_new[i][0], combine_i,
                         sort_new[i][2]])


    return new_list, combine_list


def inside_staff_all(staff_up, staff_down, new_list, del_list,
                     combine_list, n, image, staff_interval, img_h,
                     staff_over_up, staff_over_down):
    """
    new_list = 최종적으로 결정될 리스트
    combine_list = 노트가 더 합쳐질 수 있는지 비교하는 리스트
    n = combine_list 의 반복자 , 현재 판단할 combine_list 의 인덱스 값

    combine_list 에서 제거 될때
    마지막으로 이 노트가 오선줄 안에 들어가는 노트인지 판단 후 넣는다.
    """
    index = combine_list[n][1]

    j = 0
    while True:
        if j == len(new_list[index]):
            break

        stem_up_h = new_list[index][j][3]
        stem_down_h = new_list[index][j][4]

        # 1번 방법 : 스템이 오선줄 안에 들어오는지 아닌지 판단 여부에 따라 해당 노트를
        #           오선줄 안에 들일지 아닐지를 판단한다.
        result = inside_staff_1(staff_up, staff_down,stem_up_h,
                                stem_down_h, staff_over_up, staff_over_down)

        if result is True:
            pass

        else:
            # 2번 방법 : 노트 중 오선줄 (범위 +- 2.25x)안에
            #           들어오는 것이 있는지 확인한다.
            result = inside_staff_2(staff_up, staff_down, new_list,
                                    index, staff_interval, j)

            if result is True:
                pass

            else:
                # 3번 방법 : blank 가 있다고 가정 후
                w = new_list[index][j][0]
                h = new_list[index][j][1]

                result = inside_staff_3(w, h, image, staff_interval,
                                        staff_up, staff_down, img_h)
                if result is True:
                    pass

                else:
                    # new_list 에 있는 인덱스 값을 지운다
                    del new_list[index][j]
                    j -= 1
        j += 1

    # 리스트 개수가 0일 경우 (다 지워진 경우)
    # del_list 에 추가한다
    if len(new_list[index]) == 0:
        del_list.append(combine_list[n][1])

    del combine_list[n]

    return combine_list, del_list


def inside_only_staff_1(staff_up, staff_down, stem_up_h, stem_down_h,
                   staff_over_up, staff_over_down):
    """
    해당 노트가 스태프 안으로 들어올 수 있는지 확인하는 방법 중
    1번째 방법이다.

    스템이 오선줄 안에 오는지 아닌지 판단 여부에 따라 해당 노트를
    오선줄 안에 들일지 아닐지를 판단한다.

    stem_down_h (아래쪽 스템) 가 staff_up (오선 맨 위쪽 줄) 보다
    같거나 (겹치거나) 클 경우 (더 아래인 경우)

    or

    stem_up_h (위쪽 스템) 가 staff_down (오선 맨 아래쪽 줄) 보다
    같거나 (겹치거나) 작을 경우 (더 위인 경우)

    스템이 오선줄에 걸치는 형태이므로 해당 노트은 오선줄 안에 들어온다고 판단
    """
    # 스템의 아래쪽이 위쪽 오선 보다 작을 경우 (더 위일 경우)
    # 스템의 위쪽이 아래쪽 오선 보다 클 경우 (더 아래일 경우)
    # 둘중 하나라도 만족하게 되면 오선에 들어오지 않은 것이므로 not 으로 부정한다.
    result = False

    # 아래 조건을 만족한다면 스템값이 위쪽 오선에 닿거나, 아래쪽 오선에 닿는지 확인
    if not stem_down_h < staff_up and not stem_up_h > staff_down:
        result = True

    return result


def inside_staff_1(staff_up, staff_down, stem_up_h, stem_down_h,
                   staff_over_up, staff_over_down):
    """
    해당 노트가 스태프 안으로 들어올 수 있는지 확인하는 방법 중
    1번째 방법이다.

    스템이 오선줄 안에 오는지 아닌지 판단 여부에 따라 해당 노트를
    오선줄 안에 들일지 아닐지를 판단한다.

    stem_down_h (아래쪽 스템) 가 staff_up (오선 맨 위쪽 줄) 보다
    같거나 (겹치거나) 클 경우 (더 아래인 경우)

    and

    stem_up_h (위쪽 스템) 가 staff_down (오선 맨 아래쪽 줄) 보다
    같거나 (겹치거나) 작을 경우 (더 위인 경우)

    스템이 오선줄에 걸치는 형태이므로 해당 노트은 오선줄 안에 들어온다고 판단
    """
    # 스템의 아래쪽이 위쪽 오선 보다 작을 경우 (더 위일 경우)
    # 스템의 위쪽이 아래쪽 오선 보다 클 경우 (더 아래일 경우)
    # 둘중 하나라도 만족하게 되면 오선에 들어오지 않은 것이므로 not 으로 부정한다.
    result = False

    # 아래 조건을 만족한다면 스템값이 위쪽 오선에 닿거나, 아래쪽 오선에 닿는지 확인
    if not stem_down_h < staff_up and not stem_up_h > staff_down:
        t_or_f = inside_staff_4(staff_over_up, staff_over_down, stem_up_h, stem_down_h)

        if t_or_f is True:
            result = True

    return result


def inside_staff_2(staff_up, staff_down, new_list,
                   index, staff_interval, i):
    """
    노트 중 오선줄 (범위 +- 2.25x)안에
    들어오는 것이 있는지 확인한다.

    하나라도 있다면 오선줄 안에 들어오는 것으로 간주
    """

    result = False

    start = staff_up - (staff_interval * 2.25)
    end = staff_down + (staff_interval * 2.25)

    if start <= new_list[index][i][1] <= end:
       result = True

    return result


def inside_staff_3(w, h, image, staff_interval,
                   staff_up, staff_down, img_h):
    """

    노트중 blank 가 있다고 가정하고
    흰 픽셀 공백이 (스태프 사이의 거리 x 1.3)
    이상으로 많을 시 해당 노트에 안들어 온다고
    판단 후 제외 시킨다. (오류가 있을 수 있음)

    """
    # 계산 오류가 날 수 있으므로 변수 방지 차원으로
    # 1.2배 까지 계산 범위를 넓인다.
    staff_up -= round(staff_interval / 2) - 5
    staff_down += round(staff_interval / 2) + 5

    staff_interval = round(staff_interval * 1.2)

    result = False

    c = 0

    # 이미 노트 자체가 오선 안에 들어왔다면
    if staff_up <= h <= staff_down:
        result = True

    # 노트의 높이가 오선 윗쪽 보다 더 높을 경우
    elif staff_up > h:
        while True:
            h += 1

            if staff_up <= h:
                result = True
                break

            elif c > staff_interval:
                result = False
                break

            elif image[h][w] == 255:
                c_1, start, end = count_255(w, h, img_h, image)
                # 오선줄 사이의 값 보다 더 많이 나간다면

                c += c_1
                if c > staff_interval:
                    result = False
                    break

                # 계산한 값이 오선 범위안에 들어왔다면
                elif staff_up <= end <= staff_down:
                    result = True
                    break

                else:
                    c_2, start, end = count_0_ver_2(w, end + 1, img_h, image)
                    middle = round((start + end) / 2)
                    # 계산을 빠르게 하기 위해

                    s = is_blank(image, w, start)
                    e = is_blank(image, w, end)
                    m = is_blank(image, w, middle)

                    if s is True or e is True or m is True:
                        h += c_1 + c_2
                        c = 0
                        continue

                    else:
                        h += c_1 + c_2
                        c += c_2

            else:
                continue

    # 노트의 높이가 오선 아래쪽 보다 더 낮을 경우
    elif staff_down < h:
        while True:
            h -= 1

            if h <= staff_down:
                result = True
                break

            elif c > staff_interval:
                result = False
                break

            elif image[h][w] == 255:
                c_1, start, end = count_255_reverse(w, h, image)
                # 오선줄 사이의 값 보다 더 많이 나간다면

                c += c_1
                if c > staff_interval:
                    result = False
                    break

                # 계산한 값이 오선 범위안에 들어왔다면
                elif staff_up <= end <= staff_down:
                    result = True
                    break

                else:
                    c_2, start, end = count_0_reverse_ver_2(w, end - 1, image)
                    middle = round((start + end) / 2)
                    # 계산을 빠르게 하기 위해

                    s = is_blank(image, w, start)
                    e = is_blank(image, w, end)
                    m = is_blank(image, w, middle)

                    if s is True or e is True or m is True:
                        h -= c_1 + c_2
                        c = 0
                        continue

                    else:
                        h -= c_1 + c_2
                        c += c_2

            else:
                continue

    return result


def is_blank(image, w, h):
    """
    blank 가 있는지 확인하기 위해 w 양쪽으로 +- 20
    을해서 모두 검은 픽셀 (직선 모양) 이라면 blank 로 인정한다
    """
    left = False
    right = False
    blank = False

    # left 먼저 blank 인지 확인
    for i in range(1, 21):
        if image[h][w - i] == 0:
            if i == 20:
                left = True
                break
        else:
            break

    # left 가 T 면 right 도 계산
    if left is True:
        for i in range(1, 21):
            if image[h][w + i] == 0:
                if i == 20:
                    right = True

            else:
                break

        if right is True:
            blank = True

    return blank


def inside_staff_4(staff_over_up, staff_over_down, stem_up_h, stem_down_h):
    """
    해당 노트가 스태프 안으로 들어올 수 있는지 확인하는 방법 중
    4번째 방법이다.

    스템이 그 전 오선줄에 겹치거나, 다음 오선줄에 겹치는 경우
    이 쪽에 쓰이는 노트가 아니라고 판단한다
    """
    # 스템의 아래쪽이 위쪽 오선 보다 작을 경우 (더 위일 경우)
    # 스템의 위쪽이 아래쪽 오선 보다 클 경우 (더 아래일 경우)
    # 둘중 하나라도 만족하게 되면 오선에 들어오지 않은 것이므로 not 으로 부정한다.
    result = False

    if not stem_up_h < staff_over_up and not stem_down_h > staff_over_down:
        result = True

    return result


def count_0_ver_2(w_i, h_i, h, image):
    count = 0
    start = h_i
    end = 0

    while True:
        # h 끝 + 1 에 도달한 경우 w값 올리고 h값 원점으로
        if h_i == h:
            end = h_i - 1
            break

        elif image[h_i][w_i] == 0:
            h_i = h_i + 1
            count = count + 1
            continue

        elif image[h_i][w_i] != 0:
            end = h_i - 1
            break

    return count, start, end


def count_0_reverse_ver_2(w_i, h_i, image):
    count = 0
    start = h_i

    while True:
        # h 가 -1에 도달한 경우 w값 올리고 h값 원점으로
        if h_i <= -1:
            end = h_i + 1
            break

        elif image[h_i][w_i] == 0:
            h_i = h_i - 1
            count = count + 1
            continue

        elif image[h_i][w_i] != 0:
            end = h_i + 1
            break

    return count, start, end


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

    return count, start, end


def count_255_reverse(w_i, h_i, image):
    count = 0
    start = h_i

    while True:
        # h 가 -1에 도달한 경우 w값 올리고 h값 원점으로
        if h_i == -1:
            end = h_i + 1
            break

        elif image[h_i][w_i] != 0:
            h_i = h_i - 1
            count = count + 1
            continue

        elif image[h_i][w_i] == 0:
            end = h_i + 1
            break

    return count, start, end


def delete_list(result, del_list):
    for i in range(0, len(del_list)):
        del result[del_list[i] - i]

    return result


def del_list_all(del_list, result):
    for i in range(0, len(del_list)):
        del result[del_list[i] - i]

    return result


def combine_quarter_note_head(sort_new):
    result = []

    for i in range(0, len(sort_new)):

        # 무작위로 합쳐진 4분음표를 h(높이) 순서대로 정렬을 시킨다
        # h 값이 많이 다른 경우엔 다른 노트임을 알아내기 위한 방법이다
        sort_new[i].sort(key=lambda x: x[1])
        make_one_note = [sort_new[i][0]]
        note = []

        for r in range(0, len(sort_new[i])):

            try:
                next_note = sort_new[i][r + 1]
            # 더이상 다음 노트가 없을 경우
            except IndexError:
                if len(make_one_note) >= 2:
                    result_note = combine_note(make_one_note)
                    note.append(result_note)

                else:
                    note.append(make_one_note[0])
                    # result.append(sort_new[i])

            else:
                # 다음 노트와의 h 차이가 5이하 이며,
                # 이름이 같다면
                if next_note[1] - sort_new[i][r][1] <= 5 and \
                    next_note[2][:-2] == sort_new[i][r][2][:-2]:
                    make_one_note.append(sort_new[i][r + 1])
                # h 차이 5이상이라면 다른 노트라고 생각 후
                # 현재 까지 합한 노트를 합쳐서 한 노트로 만든 뒤
                # note (노트 결합 리스트)에 넣는다
                # 그리고 다시 결합해야할 노트들을 모을 make_one_note 에
                # 다시 새로운 노트를 넣으며 시작한다
                else:
                    # 결합해야할 노트가 있다면
                    if len(make_one_note) >= 2:
                        result_note = combine_note(make_one_note)
                        note.append(result_note)
                        make_one_note = [sort_new[i][r + 1]]
                    # make_one_note 에 노트가 1개 이하 라면
                    # combine 을 굳이 할 필요가 없으므로 아래와 같이 바로
                    # note 에 넣는다
                    else:
                        note.append(make_one_note[0])
                        make_one_note = [sort_new[i][r + 1]]

        result.append(note)


    return result


def combine_note(make_one_note):

    """
    가장 낮은 번호를 제일 인식률이 좋은 (중점에 가까운) 이미지 이므로
    가장 낮은 번호의 인덱스만 빼와서 한개로 만든다
    """
    lower = 100  # 100 개 이상 있지는 않것지
    for i in range(0, len(make_one_note)):
        num = int(make_one_note[i][2][-1])

        if num < lower:
            lower_i = i
            lower = num

    result = make_one_note[lower_i]

    return result


def sort_scale(result, clef, real_staff_interval, start_staff_line, scale_dic):
    result_sort_scale = []

    if clef == 'treble_clef':
        # 오선줄 맨 윗선 기준을 start 로 잡는다
        start = 38
    elif clef == 'bass_clef':
        # 위와 동일
        start = 26

    for i in range(0, len(result)):
        if result[i][0][2].find('note') > -1 \
                or result[i][0][2].find('sharp') > -1 \
                or result[i][0][2].find('flat') > -1 \
                or result[i][0][2].find('natural') > -1:
            result_all = []
            result[i].sort(key=lambda x: x[1], reverse=True)
            for r in range(0, len(result[i])):
                # 스타트 기준점 스태프 라인으로부터 얼마나 떨어져 있는지
                comparison = abs(start_staff_line - result[i][r][1])

                # 그 기준을 스태프 라인 간격으로 나누므로써
                # 스타트로부터 얼마나 올려야 스케일이 나오는지 계산
                scale_up_down = round(comparison / real_staff_interval)

                if result[i][r][1] >= start_staff_line:
                    scale_count = start - scale_up_down

                else:
                    scale_count = start + scale_up_down
                # flat 가운데 위치가 플랫의 음계보다 살짝 위이므로 아래로 내린다.
                if result[i][0][2].find('flat') > -1:
                    scale_count -= 1

                new_list = list(result[i][r])
                new_list.append(scale_count)
                try:
                    new_list.append(scale_dic[scale_count])
                except IndexError:
                    new_list.append('None')
                    new_list = list(new_list)
                    result_all.append(new_list)
                else:
                    new_list = list(new_list)
                    result_all.append(new_list)

            result_sort_scale.append(result_all)

        elif result[i][0][2].find('inside') > -1:
            if result[i][0][2].find('treble') > -1:
                start = 38

            elif result[i][0][2].find('bass') > -1:
                start = 26

        else:
            result_sort_scale.append(result[i])
            continue

    return result_sort_scale


def sort_all(staff_number, all_symbol_tuple_list, staff_lines
             , half_staff_interval, staff_interval, image, img_h):
    if staff_number == 1:
        start = 0

    else:
        start = staff_lines[((5 * (staff_number - 1)) - 1)] + \
                half_staff_interval

    if staff_number % 2 == 0:  # 짝수
        clef = 'bass_clef'

    else:
        clef = 'treble_clef'
    # 오선줄의 마지막 끝을 최대 아래쪽 오선의 반 쯤 올라와 있을 수 있으므로 범위를 여기까지 잡는다
    end = staff_lines[staff_number * 5] - half_staff_interval
    """
    한 오선줄을 지정해서 그전 오선줄, 다음 오선줄에 +- staff_interval 을 해서 
    (그전/다음 오선줄에 걸친 노트헤드 인식을 안하기 위해)
    
    그 사이에 해당되는 좌표를 가진 모든 기호들을 따로 분류 
    """
    # 어떤것만 빼야되는지 구분한다.
    sort_new = sort_list(start, end, all_symbol_tuple_list)

    # 분리 후 그 중에서 note / blank 에 스템의 값을 추가한다
    # (노트에 추가되는 값) : stem_top_h, stem_end_h, stem_w (해당 w)
    result = make_stem(sort_new, image, img_h)

    """
    합치는 기준 
    
    1. 이름 같고
    
    2. 스템값 비슷하고 
    
    3. w 35 내외 
    
    """
    # 계산할 범위 중 시작 h값 == 스태프 라인의 시작 값
    staff_start = staff_lines[(staff_number - 1) * 5]
    # 계산할 범위 중 끝 h값 == 스태프 라인의 끝 값
    staff_end = staff_lines[((staff_number - 1) * 5) + 4]
    # 맨 처음 스태프 인 경우 이미지의 맨 윗 y좌표 0 로 설정
    if (staff_number - 1) * 5 == 0:
        staff_over_up = 0
    # 그것이 아니라면 현재 스태프 에서 윗 스태프의 가장 아랫부분을 위쪽 인식 범위로 설정
    else:
        staff_over_up = staff_lines[((staff_number - 1) * 5) - 1]
    # 현재 스태프에서 아래 스태프의 가장 윗 부분을 아래쪽 인식 범위로 설정
    staff_over_down = staff_lines[((staff_number - 1) * 5) + 4 + 1]

    # 범위내에 해당되지 않는 노트 선별후 / 노트 결합 후 결과값, del 리스트를 만든다
    # 노트를 제외하고 w, h 차이가 5 이하인 여러 심볼 들도 합친다.
    result, del_list = sort_w_list(result, staff_start, staff_end, image,
                                   staff_interval, img_h, staff_over_up, staff_over_down)

    # del 리스트에 있는 것들을 바탕으로 result 리스트에 있는 것들을 지운다.
    result = delete_list(result, del_list)

    # 스케일 (음계) 를 알아낸다.
    result = sort_scale(result, clef, half_staff_interval,
                        staff_lines[(staff_number - 1) * 5], scale_dic)

    # bass clef 라면 점 2개가 뒤에 바로 찍히므로 없애준다 (아무 의미 없기 때문)
    if result[0][0][2] == 'bass_clef':
        i = 1

        while True:
            if result[i][0][2] == 'dot':
                del result[i]
                i += 1

            else:
                break

    return result
