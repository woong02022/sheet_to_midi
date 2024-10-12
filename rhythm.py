from add_beam_list import *
from line_list import *
import copy

beam_list = [
    '4th',
    '8th',
    '16th',
    '32th',
    '64th',
    '128th'
]


note = {
    '1': 4,
    '2': 2,
    '4': 1,
    '8': 0.5,
    '16': 0.25,
    '32': 0.125,
    '64': 0.0625,
    '128': 0.03125
}

def find_near_left_note_or_rest(result, i, note_rest=None):

    while True:
        i -= 1

        if i == -1:
            i = 'none'
            break

        elif note_rest == 'note':
            if result[i][0][2].find('note') >= 0:
                break

        elif note_rest == 'rest':
            if result[i][0][2].find('note') >= 0:
                break

        else:
            if result[i][0][2].find('note') >= 0 \
                    or result[i][0][2].find('rest') >= 0:
                break

    return i


def find_near_right_note_or_rest(result, i, note_rest=None):

    while True:
        i += 1

        if i > len(result) - 1:
            i = 'none'
            break
        # 노트만 검색
        elif note_rest == 'note':
            if result[i][0][2].find('note') >= 0:
                break
        # 쉼표만 검색
        elif note_rest == 'rest':
            if result[i][0][2].find('note') >= 0:
                break

        else:
            if result[i][0][2].find('note') >= 0 \
                    or result[i][0][2].find('rest') >= 0:
                break

    return i


def count_up(image, h, w):
    count = 0
    skip = 0
    i = 0

    while True:
        if skip >= 5:
            break

        elif image[h - i][w] == 0:
            skip = 0
            count += 1
            i += 1

        else:
            skip += 1

    return count


def count_down(image, h, w):
    count = 0
    skip = 0
    i = 0

    while True:
        if skip >= 5:
            break

        elif image[h + i][w] == 0:
            skip = 0
            count += 1
            i += 1

        else:
            skip += 1

    return count


def count_beam_triplet(image, w_i, h_i, h):
    beam_count = 0

    m = 1  # 빔과 빔 사이의 격차 허용이며 아래와 같이 9 이하까지 이다.

    while True:

        if m >= 9:
            break

        elif image[h_i + m][w_i] == 255:
            m = m + 1
            continue

        elif image[h_i + m][w_i] == 0:
            a, h_i, count, c, d = count_0(w_i, h_i + m, h, image)

            if 10 <= count <= 26:
                beam_count = beam_count + 1
                m = 1
                continue

            elif count <= 3:
                m = m + count
                continue

    return beam_count


def count_beam_reverse_triplet(image, w_i, h_i):
    beam_count = 0

    m = 1  # 빔과 빔의 간격차이

    while True:

        # m > 빔과 빔의 간격차이를 적는곳
        if m >= 9:
            break

        elif image[h_i - m][w_i] == 255:
            m = m + 1
            continue

        elif image[h_i - m][w_i] == 0:
            a, h_i, count, c, d = count_0_reverse(w_i, h_i - m, image)

            if 10 <= count <= 26:
                beam_count = beam_count + 1
                m = 1
                continue

            elif count <= 3:
                m = m + count  # 여기서 plus 1을 안해줄경우 오류가 생길수 있음 멈춰있는 곳이 0 일수 도 있기에
                continue

    return beam_count


def distinguish_triplet(result_1, result_2, image, h, staff_lines, staff_num):
    """
    triplet 정보를 받아 위(1) 혹은 아래(2) 어디에 적용시킬지
    판단 후 note_number 까지 내보내는 함수이다
    """
    # result_1 (triplet 기준 위쪽 오선용 스태프 h 값)
    # (위쪽 오선이므로 맨 아래 줄 값을 쓴다)
    # 현재 staff_num 은 result_2 기준이므로 -1 을 해서 result_1 에 맞춘다
    staff_1 = staff_lines[((staff_num - 1) * 5) - 1]

    # result_2 는 아래쪽 오선이므로 맨 위쪽 줄 값을 쓴다.
    staff_2 = staff_lines[(staff_num - 1) * 5]

    i = 0  # result_1 반복자 사용
    o = 0  # result_2 반복자 사용
    while True:
        if i >= len(result_1):
            break

        # 만약 1에서 triplet 을 찿았다면
        if result_1[i][0][2].find('triplet') >= 0:

            # 1에 있는 triplet 정보를 2에서 찿아내 해당 o 값 생성
            o = find_in_2(result_1[i][0], result_2, o)

            # 2 랑 비교했을때 같은 triplet 이 없다면
            # 바로 1에 적용 시킨다
            if o == 'none':
                left_1 = find_near_left_note_or_rest(result_1, i, 'note')
                right_1 = find_near_right_note_or_rest(result_1, i, 'note')

                bool_1, l_index_1, r_index_1, stem_u_d_1 = \
                    th_find(result_1, i, left_1, right_1, image)

                tri_num = int(result_1[i][0][2][-1])

                result_1 = start_end_triplet(result_1, l_index_1, r_index_1, tri_num)

                i += 1
                o = 0
                continue

            # 같은 triplet 이 있는 경우, 비교해서 어디에 적용되는지 알아낸다. (result)
            # 그 후 적용될 범위까지 알아낸다 (start, end)
            else:
                # triplet 을 찿았으므로 o_2 를 o로 한다.
                # o_2 를 o로 바꾸므로써, result_2 의 계산 범위를 줄인다.
                one_two, start, end = \
                    compare_up_down(result_1, result_2, i, o,
                                    image, h, staff_1, staff_2)

                tri_num = int(result_1[i][0][2][-1])
                if one_two is None:
                    pass

                # result_1 에 적용시키는 경우
                elif one_two == 1:
                    # 위에서 찾은 인덱스 적용 범위를 해당 result 에 적용 시킨다
                    # 맨 뒤에다 붙이며 해당 정수값은 이미 triplet 이 적용된
                    # note_number 가 될 숫자이다
                    # ex) [[2851, 669, 'quarter_note_head_4'].... , 0.333]
                    result_1 = start_end_triplet(result_1, start, end, tri_num)
                    del result_2[o]

                # result_2 에 적용시키는 경우
                elif one_two == 2:
                    result_2 = start_end_triplet(result_2, start, end, tri_num)
                    del result_2[o]

            i += 1

        else:
            i += 1

    return result_1, result_2


def start_end_triplet(result, start, end, tri_num):
    """
    마지막으로 이 트리플렛이 현재 적용범위랑
    맞는지, 최종적으로 확인을 한다. 방법은 아래와 같다

    1. start ~ end 인덱스 까지 가장 낮은 note_number 를 구한다.

    2. 가장 작은 note_num x tri_num 값을 구한다.

    3. 1번 방법에서 순회를 할때 모든 note_number 를 다 합한다.

    4. 2번에서 구한 값과 3번과 값이 똑같다면 적용할 수 있는것으로 판단

    5. (현재 note_num / 가장 낮은 note_number) *
    round(가장 높은 note_number 애서 한단계 높은 note_number / tri_num), 3)
    이 공식으로 마무리 한다.

    # 가장 높은 note_num 에서 한단계 높다 예시 >
    8분음표 >> 4분음표
    """

    plus_all_num = 0
    for i in range(start, end + 1):
        if result[i][0][2].find('note') >= 0 or \
                result[i][0][2].find('rest') >= 0:
            # 처음 반복이라면 compare (비교값) 을 만든다
            if i == start:
                lower_note_num = result[i][-1]
                higher_note_num = result[i][-1]
                plus_all_num += lower_note_num
                continue

            else:
                current_note_num = result[i][-1]
                plus_all_num += current_note_num

            # 반복을 하면서 가장 낮은 note_number 를 구한다
            if current_note_num < lower_note_num:
                lower_note_num = current_note_num
            # 또한 가장 높은 note_number 도 구한다
            elif current_note_num > higher_note_num:
                higher_note_num = current_note_num

    # 아래 구문이 T 면
    # 적용할 수 있는것으로 판단
    if lower_note_num * tri_num == plus_all_num:
        # 가장 높은 note_number 애서 한단계 높은 note_number
        divide_3 = lower_note_num * 2
        for i in range(start, end + 1):
            if result[i][0][2].find('note') >= 0 or \
                    result[i][0][2].find('rest') >= 0:

                current_note_num = result[i][-1]
                note_number = (current_note_num / lower_note_num) * \
                round(divide_3 / tri_num, 3)

                result[i][-1] = note_number

    return result


def find_in_2(tri, result_2, o):
    """ make_2 에서 make_1 이랑 같이 탐지된 동일한 triplet 을 찿는다.
        결과값은 result_2 의 o (대체 i) 값을 찿는다.
        triplet = [w, h, 'triplet']
    """

    t_w = tri[0]
    t_h = tri[1]

    while True:
        if o >= len(result_2):
            o = 'none'
            break

        if result_2[o][0][2].find('triplet') >= 0 and \
                result_2[o][0][0] == t_w and \
                result_2[o][0][1] == t_h:
            break

        else:
            o += 1

    return o


def compare_up_down(result_1, result_2, i, o, image, h, staff_1, staff_2):

    """
    1 == 위쪽에 위치해 있는 오선
    2 == 아래쪽에 위치해 있는 오선
    i = 1의 반복자
    o = 2의 반복자


    둘을 비교해 triplet 이 위, 아래중 어디에 적용이 되는것인지를 찿는다.

    1. th_find 로 양쪽으로
    ( T, F, N(none) )

    8th 이상의 연결된 빔이 존재 하는지 확인 그리고
    (맞다면 T / 아니면 F / 존재하지 않는다면 None)


    """
    left_1 = find_near_left_note_or_rest(result_1, i)
    right_1 = find_near_right_note_or_rest(result_1, i)
    left_2 = find_near_left_note_or_rest(result_2, o)
    right_2 = find_near_right_note_or_rest(result_2, o)

    # 양쪽에 같은 (4th 제외) ?th 가 있다면 bool = True 가 된다
    # 양쪽의 범위를 알아낸다.
    bool_1, l_index_1, r_index_1, stem_u_d_1 = \
        th_find(result_1, i, left_1, right_1, image)

    bool_2, l_index_2, r_index_2, stem_u_d_2 = \
        th_find(result_2, o, left_2, right_2, image)

    # 둘다 connect = T 라면 (지정선 존재 x)
    # 스템 (=빔) 값 h 가 어느쪽에 tri 더 가깝냐에 따라 결정된다.
    # 서로 어느 방향의 스템이 빔인지는 th_find 에서 u_d 변수가 알려줄 수 있다.
    if bool_1 and bool_2 is True:
        h_1 = result_1[left_1][0][stem_u_d_1]
        h_2 = result_2[left_2][0][stem_u_d_2]

        tri_h = result_1[i][0][1]

        diff_h_1 = abs(h_1 - tri_h)
        diff_h_2 = abs(h_2 - tri_h)

        # 1 쪽이 더 가깝다면
        # 최종 결정 >> 1
        if diff_h_1 < diff_h_2:
            result = 1
            start = l_index_1
            end = r_index_1
        # 2 쪽이 더 가깝다면
        # 최종 결정 >> 2
        else:
            result = 2
            start = l_index_2
            end = r_index_2

    # 1 == T/F , 2 == N (적용 자체가 불가능) 일때
    # 바로 triplet 을 1 에 선정한다
    elif bool_1 is not None and bool_2 is None:
        result = 1
        start = l_index_1
        end = r_index_1

    # 위와 반대의 경우 2 에 선정한다
    elif bool_1 is None and bool_2 is not None:
        result = 2
        start = l_index_2
        end = r_index_2

    # 어느 한쪽이라도 connect = F일 경우 (둘다 F도 포함)
    elif (bool_1 is True and bool_2 is False) or \
            (bool_1 is False and bool_2 is True) or \
            (bool_1 is False and bool_2 is False):
        # 어디부터 어디까지 적용시킬 건지
        # start (시작점), end (끝점)
        up_down = find_tri_line(result_1, result_2, i, l_index_1, r_index_1,
                                l_index_2, r_index_2, image)

        # 마지막 방법으로 bool == T 라면 빔의 h 값을 쓰고
        # bool = F 라면 staff (1 = 맨 아래 , 2 = 맨 위) h 값을 써서
        # tri_h 값이랑 비교했을때 더 가까운쪽을 선택한다.
        if up_down is None:
            if bool_1 is True:
                h_1 = result_1[left_1][0][stem_u_d_1]
            else:
                h_1 = staff_1

            if bool_2 is True:
                h_2 = result_2[left_2][0][stem_u_d_2]
            else:
                h_2 = staff_2

            tri_h = result_1[i][0][1]

            diff_h_1 = abs(h_1 - tri_h)
            diff_h_2 = abs(h_2 - tri_h)
            # 1 쪽이 더 가깝다면
            # 최종 결정 >> 1
            if diff_h_1 < diff_h_2:
                result = 1
                start = l_index_1
                end = r_index_1
            # 2 쪽이 더 가깝다면
            # 최종 결정 >> 2
            else:
                result = 2
                start = l_index_2
                end = r_index_2

        elif up_down == 'up':
            result = 1
            start = l_index_1
            end = r_index_1

        elif up_down == 'down':
            result = 2
            start = l_index_2
            end = r_index_2

    else:
        result = None
        start = None
        end = None

    return result, start, end


def th_find(result, i, left, right, image):
    """
    왼쪽, 오른쪽에 (4th 는 제외)  8th, 16th 등의 노트헤드가 있고
    서로가 beam 으로 연결되 있는 형태이면
    (가운데에 있는 형태일수도 있으므로 w는 크게 잡는다)
    True 를 반납

    또한 노트의 적용 범위까지 알아낸다
    (완벽한 적용 범위라고 보기 힘든게 빔의 경우 6개 일수도 있고
    여러개의 노트중 3개를 따로 골라내야 할 수도 있다)
    """
    t_f = False

    if left == 'none' or right == 'none':
        return None, None, None, None


    left_note_num = result[left][-1]

    right_note_num = result[right][-1]

    # 왼쪽이 더 클때
    if left_note_num > right_note_num:
        num_difference = left_note_num / right_note_num
    # 오른쪽이 더 크거나 같을때
    else:
        num_difference = right_note_num / left_note_num

    # connect = T / F (연결되면 T / 아니면 F)
    # u_d = up/down 인덱스 정보 (connect = F 면 사용 금지)
    connect, stem_u_d = is_connect_beam(result, left, right, image)

    # 양쪽에 (4th 제외) 8 이상의 th 등의 노트/쉼표 가 있는지,
    # 양 끝 노트 차이가 없거나, 2배 일때,
    # 빔으로 연결되어 있는지
    # 위 조건들을 만족한다면 True 를 내보낸다.
    if left_note_num <= 0.5 and right_note_num <= 0.5 \
            and (num_difference == 1 or num_difference == 2) and \
            connect is True:
        t_f = True

    # 노트 적용 범위를 알아낸다.
    middle_val = result[i][0]
    left_val = result[left][0]
    right_val = result[right][0]

    left_interval = abs(middle_val[0] - left_val[0])
    right_interval = abs(middle_val[0] - right_val[0])

    # 빔이 연결되어 있다면 적용 방식을 달리한다. (3개 이상인 경우도 있으므로)
    # accept_index_1 = 적용 맨 왼쪽 지점
    # accept_index_2 = 적용 맨 오른쪽 지점
    if connect is True:
        # 트리플렛이 ?연음인지 구한다.
        tri_num = int(result[i][0][2][-1])

        # 짝수 라면 트리플렛 양쪽에 있는 노트로 시작한다
        if tri_num % 2 == 0:
            count = 0
        # 홀수 라면 가운데 노트 선정 후 그 주변에 있는 노트로 시작한다
        else:
            if left_interval <= right_interval:
                left = find_near_left_note_or_rest(result, left)

            else:
                right = find_near_right_note_or_rest(result, right)

            count = 1

        accept_index_1, accept_index_2 = \
            beam_accept_tri(result, left, right, stem_u_d, image, count, tri_num)

    else:
        # 차이가 1이라면 양쪽 노트가 같은 노트 이므로
        # 가운데를 찿아서 양 끝 노트를 찿는다 (총 3개)
        if num_difference == 1:
            # 왼쪽에 더 가깝다면 왼쪽 노트에서 한칸 더 왼쪽에 있는 노트 / 쉼표가 적용 인덱스 값
            if left_interval <= right_interval:
                accept_index_1 = find_near_left_note_or_rest(result, left)
                accept_index_2 = right

            else:
                accept_index_1 = left
                accept_index_2 = find_near_right_note_or_rest(result, right)

        # 차이가 2이라면 양쪽 노트가 다른 노트 이므로
        # triplet 기준 양 끝 노트가 적용 지점
        elif num_difference == 2:
            accept_index_1 = left
            accept_index_2 = right

        else:
            t_f = None
            accept_index_1 = None
            accept_index_2 = None

    # 인덱스 번호로 바꾼다
    if stem_u_d == 'up':
        stem_u_d = 3
    elif stem_u_d == 'down':
        stem_u_d = 4

    return t_f, accept_index_1, accept_index_2, stem_u_d


def is_connect_beam(result, l_i, r_i, image, up_down=None):
    """
    두개의 노트 값을 받고, 서로 beam 으로 연결이 되있는지 확인

    연결되있으면 True, 안되있으면 False

    'up' == 3 (인덱스) 'down' == 4

    return 값으로는 connect 의 T/F ,
    up/down (스템에서 위쪽이 빔인지 아래쪽이 빔인지)
    """

    # 일단 먼저 서로 노트임을 확인해야 한다.
    # (노트가 아니라면 스템 값 인덱스가 존재하지 않으므로 인덱스 에러가 일어남)
    if result[l_i][0][2].find('note') >= 0 and \
            result[r_i][0][2].find('note') >= 0:
        # 스템 위 값, 아래값 한번씩 계산
        for h in range(0, 2):
            if h == 0:
                if up_down is None or up_down == 'up':
                    u_d = 3 # 스템 위쪽 인덱스 값
                    # 빔 위쪽 이므로 위쪽 라인이 잡히므로
                    # 빔의 가운데 쯤 될려면 + 6 이여야 함
                    correction = 6 # 보정값 +6
                # up_down == 'down' 인 경우 검색 중지
                else:
                    continue

            elif h == 1:
                if up_down is None or up_down == 'down':
                    u_d = 4 # 스템 아래쪽 인덱스 값
                    # 빔 아래쪽 이므로 아래쪽 라인이 잡히므로
                    # 빔의 가운데 쯤 될려면 - 6 이여야 함
                    correction = -6
                # up_down == 'up' 인 경우 검색 중지
                else:
                    break

        # 일단 어느 스템 위쪽이 빔인지 아래쪽이 빔인지 알 수 없으므로
        # 먼저 위쪽 값만 모아서 계산해 본다.

            # stem = (h, w)
            stem_1 = (result[l_i][0][u_d], result[l_i][0][5])
            stem_2 = (result[r_i][0][u_d], result[r_i][0][5])

            predict_line_list = get_line_points_list(stem_1, stem_2)

            connect = True

            for p in range(0, len(predict_line_list)):
                p_w = predict_line_list[p][1]
                p_h = predict_line_list[p][0] + correction

                if image[p_h][p_w] == 0:
                    continue
                # 하나라도 끊김이 있다면 false 로 처리 한다
                else:
                    connect = False
                    break
            # h == 1 (아래쪽 빔) 을 탐색하지 않아도 찾았다면 넘어갈 수 있게 한다
            if connect is True:
                break

    else:
        connect = False
        h = 1

    if h == 0:
        up_down = 'up'
    elif h == 1:
        up_down = 'down'

    return connect, up_down


def beam_accept_tri(result, left, right, up_down, image, count, tri_num):
    """
    빔이 있는 triplet 이라면 3, 6개 등등 범위가 다양하므로

    triplet 양쪽으로 적용 지점을 찿는다

    적용 기준은 양쪽 노트가 서로 같은 th 여야 하며, connect_beam = T 여야 한다

    양쪽으로 찿다가 한쪽이 없는 경우 다른 한쪽까지 적용 후 종료

    두쪽 다 찾다가 둘다 없는 경우 바로 종료

    """

    while True:
        # 현재 인덱스 값에서 양쪽 노트의 인덱스를 알아낸다.
        next_left = find_near_left_note_or_rest(result, left, 'note')
        next_right = find_near_right_note_or_rest(result, right, 'note')

        if next_left == 'none':
            left_connect = False
            left_th_same = False
        else:
            left_connect, l_u_d = \
                is_connect_beam(result, next_left, left, image, up_down)

            l_num = result[left][-1]

            n_l_num = result[next_left][-1]

            left_th_same = l_num == n_l_num

        if next_right == 'none':
            right_connect = False
            right_th_same = False
        else:
            right_connect, r_u_d = \
                is_connect_beam(result, right, next_right, image, up_down)

            r_num = result[right][-1]

            n_r_num = result[next_right][-1]

            right_th_same = r_num == n_r_num

        # next_left 가 아예 존재하지 않거나
        # 빔이 연결되있으면서, ?th 까지 같다면 next 를 현재 인덱스로 인정해 폭을 넓힌다
        if (left_connect is True and left_th_same is True) and \
                (right_connect is True and right_th_same is True):
            left = next_left
            right = next_right
            count += 2
            continue

        # next_right 가 아예 존재하지 않거나
        # 한쪽만 연결이 된 경우 그 부분까지 적용하고 반복을 중지
        elif (left_connect is True and left_th_same is True) and \
                (right_connect is False and right_th_same is False):
            # 현재 적용 범위가 tri_num (?연음) 의 배수라면
            # 지금 left 가 연결이 된다해도 적용시키지 않는다
            if count % tri_num == 0:
                # count (적용 범위가 tri_num 보다 적을 경우 continue 로 계속 진행한다.)
                if count < tri_num:
                    continue

                else:
                    break
            # 적용 범위까지 들지 않았으므로 현재 left 까지 적용시킨다
            else:
                left = next_left
                break

        elif (left_connect is False and left_th_same is False) and \
                (right_connect is True and right_th_same is True):

            if count % tri_num == 0:
                if count < tri_num:
                    continue

                else:
                    break

            else:
                right = next_right
                break

        # 둘다 연결이 안되면 바로 중지
        else:
            break

    # 최종 적용할 왼쪽 인덱스, 오른쪽 인덱스 값을 내보낸다.
    return left, right


def find_tri_line(result_1, result_2, tri_i, l_i_1, r_i_1,
                  l_i_2, r_i_2, image):

    accept_direction = None

    tri_w = result_1[tri_i][0][0]
    # tri_w 값 +- 30 으로 라인의 첫 스타트의 예상 지점을 정한다
    start_l_w = tri_w - 40
    start_r_w = tri_w + 40

    left_h = result_1[tri_i][0][1]
    right_h = result_1[tri_i][0][1]

    # [1] 스타트 지점을 찿는다
    # same == 평행
    # up == 왼쪽 : 위, 오른쪽 : 아래
    # down == 왼쪽 : 아래, 오른쪽 : 위
    for q in range(0, 3):
        if q == 0:
            direction = 'same'

        elif q == 1:
            direction = 'up'

        elif q == 2:
            direction = 'down'

        start_l_h, start_r_h = find_start_point(result_1, tri_i, start_l_w, start_r_w,
                                                left_h, right_h, image, direction)

        # 못 찾은 경우 다음으로 넘어간다
        if start_l_h is None or start_r_h is None:
            continue

        else:
            break

    # start 지점을 찾았다면 >>
    # [2] end 지점을 찾는다
    if not (start_l_h is None or start_r_h is None):
        end_l_w, end_l_h, accept_direction_l = \
            find_end_point(image, start_l_w, start_l_h, 'left', direction)

        end_r_w, end_r_h, accept_direction_r = \
            find_end_point(image, start_r_w, start_r_h, 'right', direction)

        # 맨 마지막 휘어진 방향이 존재하며 왼쪽과 오른쪽이 같아야만 인정이다
        if (accept_direction_l is not None and accept_direction_r is not None) and \
            accept_direction_l == accept_direction_r:
            # up 일 경우 1번을 사용
            if accept_direction_l == 'up':
                l_w = result_1[l_i_1][0][0]
                r_w = result_1[r_i_1][0][0]
            # down 일 경우 2번을 사용
            elif accept_direction_l == 'down':
                l_w = result_2[l_i_2][0][0]
                r_w = result_2[r_i_2][0][0]

            # 계산한 양쪽 끝 라인과 트리플렛 적용 예상 지점의
            # 차이를 계산한다
            diff_l_w = abs(l_w - end_l_w)
            diff_r_w = abs(r_w - end_r_w)

            # 차이가 50 안쪽이면 인정한다.
            if diff_l_w <= 50 and diff_r_w <= 50:
                accept_direction = accept_direction_l

    return accept_direction


    # start 지점을 못찾은 경우
    # [3] end 지점의 l, r 의 위치가 서로 같은지 확인 후
    # result 안에 들어가는 양 끝의 노트와 위치 비교 후 가깝다면
    # 최종 인정

    # triplet 양쪽에 있는 노트가 같은 종류의 노트일 경우 (th_find 에서 미리 찿는게 좋을지도)
    # 가운데를 선정해 양끝을 만들고
    # 양쪽에 있는 노트가 서로 다르며 1:2 속도 비율이라면 tri 양끝에 있는 노트를 선정 한다.

    # 사실 이 과정은 th_find 에서 미리 해서 None 같은 걸로 적용 불가능을 만들어 버려도 괜찮지
    # 않을까 생각중 어쨋든 th_find 에서 미리 양끝 노트 선정해 오자

def find_start_point(result_1, tri_i, left_w, right_w,
                     left_h, right_h, image, direction):
    """
    tri 라인을 찿을 왼쪽, 오른쪽 좌표값을 찿는다.

    """
    # 1 : 왼쪽 == 오른쪽 (평행)
    # 시작점 위치를 모르니 h 지점 += 5 단위로 찿는다

    # 찿았다는 표시로 반복 중단을 알려주기 위한 변수
    start_find = False

    if direction == 'same':
        for n in range(0, 11):
            # n == 0 일땐 h 값 변화 x
            # 1 ~ 5 까지는 위쪽 5 까지 찿아본다
            if 1 <= n <= 5:
                left_h += 1
                right_h += 1
            # 6 ~ 11 까지는 아래쪽 5 까지 찿아본다
            elif n == 6:
                left_h = result_1[tri_i][0][1] - 1
                right_h = result_1[tri_i][0][1] - 1
            elif n >= 7:
                left_h -= 1
                right_h -= 1

            if image[left_h][left_w] == 0 and \
                    image[right_h][right_w] == 0:
                start_find = True
                break

        if start_find is True:
            return left_h, right_h

        else:
            return None, None

    # 2 : 왼쪽 : 위 / 오른쪽 : 아래
    # 위아래 10 개까지 찿아본다
    elif direction == 'up':
        for n in range(0, 20):
            left_h -= 1
            right_h += 1

            # 어느 한쪽이 찿았다면 w 값이 중심이 아닐 수도 있는점을
            # 대비해서 +- 5 까지 더 찾아본 후 없다면 다음으로 패스
            if image[left_h][left_w] == 0 or \
                    image[right_h][right_w] == 0:
                # 둘다 검은 픽셀인 경우 break
                if image[left_h][left_w] == 0 and \
                        image[right_h][right_w] == 0:
                    start_find = True
                    break

                # 오른쪽만 검은 픽셀인 경우
                elif image[right_h][right_w] == 0:
                    # 왼쪽으로 5칸 더 찿아본다
                    for m in range(0, 5):
                        left_h -= 1

                        if image[left_h][left_w] == 0:
                            start_find = True
                            break

                    if start_find is True:
                        break

                # 왼쪽만 검은 픽셀인 경우
                elif image[left_h][left_w] == 0:
                    # 오른쪽으로 5칸 더 찿아본다
                    for m in range(0, 5):
                        right_h += 1

                        if image[right_h][right_w] == 0:
                            start_find = True
                            break

                    if start_find is True:
                        break

        if start_find is True:
            return left_h, right_h

        else:
            return None, None

    elif direction == 'down':
        for n in range(0, 20):
            left_h += 1
            right_h -= 1

            # 어느 한쪽이 찿았다면 w 값이 중심이 아닐 수도 있는점을
            # 대비해서 +- 5 까지 더 찾아본 후 없다면 다음으로 패스
            if image[left_h][left_w] == 0 or \
                    image[right_h][right_w] == 0:
                # 둘다 검은 픽셀인 경우 break
                if image[left_h][left_w] == 0 and \
                        image[right_h][right_w] == 0:
                    start_find = True
                    break

                # 오른쪽만 검은 픽셀인 경우
                elif image[right_h][right_w] == 0:
                    # 왼쪽으로 5칸 더 찿아본다
                    for m in range(0, 5):
                        left_h += 1

                        if image[left_h][left_w] == 0:
                            start_find = True
                            break

                    if start_find is True:
                        break

                # 왼쪽만 검은 픽셀인 경우
                elif image[left_h][left_w] == 0:
                    # 오른쪽으로 5칸 더 찿아본다
                    for m in range(0, 5):
                        right_h -= 1

                        if image[right_h][right_w] == 0:
                            start_find = True
                            break

                    if start_find is True:
                        break

        if start_find is True:
            return left_h, right_h

        else:
            return None, None


def find_end_point(image, w, h, l_r, direction):
    """
    지정선의 start point 를 찿았다면
    l_r 값 중 하나를 선택해 direction = up/down/same 에
    맞는 값으로 값의 끝을 본다.

    직선의 휘어짐 정도의 허용은 +-3 까지 허용한다
    """
    end_find = False

    # 1. 끝 포인트를 찿는다.
    while True:
        if image[h][w] == 0:
            # 왼쪽이면 왼쪽으로 가야 하므로 w 방향으로 - 1
            if l_r == 'left':
                w -= 1
            # 오른쪽은 + 1
            elif l_r == 'right':
                w += 1

        elif image[h][w] == 255:
            # up / same (방향이 바뀔 수 있음)
            # h 를 3칸 까지 위로 올려서 찿아본다
            # 없다면 이쪽이 end_point 라고 상정
            if direction == 'up' or \
                    direction == 'same':
                for n in range(0, 3):
                    if l_r == 'right':
                        h += 1
                    elif l_r == 'left':
                        h -= 1

                    if image[h][w] == 0:
                        # direction == 'same' 이면
                        # 방향이 바뀐것이므로 아래와 같이 다시 설정
                        direction = 'up'
                        break

                    elif n == 2:
                        # down 일 수 있으므로 반복을 아직 중단하지 않는다
                        if direction == 'same':
                            if l_r == 'right':
                                h -= 3
                            elif l_r == 'left':
                                h += 3

                            break

                        else:
                            # +-3 한거는 다시 원래대로 복구
                            if l_r == 'right':
                                h -= 3
                            elif l_r == 'left':
                                h += 3

                            # w 값도 그 전 으로 돌려 end 에 맞춰준다.
                            if l_r == 'left':
                                w += 1
                            elif l_r == 'right':
                                w -= 1

                            end_find = True
                # end 를 찾았으므로 현재의 w, h 값이 end_point 가 된다.
                if end_find is True:
                    break

            if direction == 'down' or \
                    direction == 'same':
                for n in range(0, 3):
                    if l_r == 'right':
                        h -= 1
                    elif l_r == 'left':
                        h += 1

                    if image[h][w] == 0:
                        # direction == 'same' 이면
                        # 방향이 바뀐것이므로 아래와 같이 다시 설정
                        direction = 'down'
                        break

                    elif n == 2:
                        # +3 한거는 다시 원래대로 복구
                        if l_r == 'right':
                            h += 3
                        elif l_r == 'left':
                            h -= 3

                        # w 값도 그 전 으로 돌려 end 에 맞춰준다.
                        if l_r == 'left':
                            w += 1
                        elif l_r == 'right':
                            w -= 1

                        end_find = True

                if end_find is True:
                    break

    # end 를 찾았으므로 현재의 w, h 값이 end_point 가 된다.
    # 각각의 변수는 다른 채널의 변수로 저장
    # 다음 계산을 할때 w, h 값이 방해가 되면 안되기 때문
    end_w = copy.deepcopy(w)
    end_h = copy.deepcopy(h)

    # 2. 어느쪽으로 휘어져 있는지 찿는다
    accept_direction = None
    count = 0
    # 위쪽 부터 계산한다.
    while True:
        end_h -= 1
        if image[end_h][end_w] == 0:
            count += 1

        elif count >= 20:
            accept_direction = 'up'
            break

        else:
            break

    count = 0
    # up 쪽을 못찾았다면 down 을 본다
    if not accept_direction == 'up':

        end_w = copy.deepcopy(w)
        end_h = copy.deepcopy(h)

        while True:
            end_h += 1

            if image[end_h][end_w] == 0:
                count += 1

            elif count >= 20:
                accept_direction = 'down'
                break

            else:
                break

    end_w = copy.deepcopy(w)
    end_h = copy.deepcopy(h)

    return end_w, end_h, accept_direction


def find_near_left_note_or_rest_2(result, i, note_rest=None):

    while True:
        i -= 1

        if i == -1:
            i = 'none'
            break

        elif note_rest == 'note':
            if result[i]['shape'].find('note') >= 0:
                break

        elif note_rest == 'rest':
            if result[i]['shape'].find('note') >= 0:
                break

        else:
            if result[i]['shape'].find('note') >= 0 \
                    or result[i]['shape'].find('rest') >= 0:
                break

    return i


def find_near_right_note_or_rest_2(result, i, note_rest=None):
    """

    :param result:
    :param i:
    :param note_rest: 노트 혹은 쉼표만 검색 하게 해준다.
    :return:
    """
    while True:
        i += 1

        if i > len(result) - 1:
            i = 'none'
            break
        # 노트만 검색
        elif note_rest == 'note':
            if result[i]['shape'].find('note') >= 0:
                break
        # 쉼표만 검색
        elif note_rest == 'rest':
            if result[i]['shape'].find('note') >= 0:
                break

        else:
            if result[i]['shape'].find('note') >= 0 \
                    or result[i]['shape'].find('rest') >= 0:
                break

    return i

# ===================== dot 적용 ====================

def find_near_left_note_or_rest_dot(result, i):
    """
    dot 버전 용

    오른쪽 근처에 있는 노트/쉼표 중
    note_number > 0 만 찿는다.

    """
    while True:
        i -= 1

        if i == -1:
            i = 'none'
            break

        if (result[i][0][2].find('note') >= 0
                or result[i][0][2].find('rest') >= 0):
            break

    return i