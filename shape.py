
distance = {
    1: 2,
    2: 2,
    3: 3,
    4: 3,
    5: 3,
    6: 3,
    7: 3,
    8: 4,
    9: 4,
    10: 4,
    11: 4,
}


# 숫자간의 차이


def up_down(number_1, number_2):
    # 여기서 부터는 숫자비교
    if number_1 <= number_2:
        return 'up'

    elif number_1 > number_2:
        return 'down'


def number_distance(octave):
    number = octave[0]
    number_2 = octave[-1]
    number_3 = abs(number - number_2)

    if number_3 >= 12:
        difference = 5

    # same 일 경우 차이는 0이다.
    elif number_3 == 0:
        difference = 2

    else:
        difference = distance[number_3]

    return difference


def right_left(finger, l_r):
    """
    만약 left 일시에는 만들어진 finger 에 대칭(반전) 을 시켜줘야
    왼손에 맞는 핑거링이 나온다. (멀티에만 적용)
    :param finger:
    :param l_r:
    :return:
    """
    if l_r == 'left':
        finger.reverse()

    return finger


# ex) making = [47, 49, 51, 52, 54, 55, 56]
def up(making, i, made_finger, l_r):
    # 다음 노트가 무엇인지 보고 끝 핑거를 정한 후 앞쪽 핑거 제작

    if (making[i - 1]['shape'] == 'down' or
        making[i - 1]['speed'] == 'fast') \
            and not i == 0:
        not_use = made_finger[-1]  # 만들때 못사용하는 핑거

    else:
        not_use = None

    current_len = len(making[i]['finger'])

    if l_r == 'right':
        made_finger = right_up_left_down(making, i, made_finger,
                                         current_len, not_use)
    elif l_r == 'left':
        made_finger = right_down_left_up(making, i, made_finger,
                                         current_len, not_use)

    return made_finger, i


def down(making, i, made_finger, l_r):
    # 다음 노트가 무엇인지 보고 끝 핑거를 정한 후 앞쪽 핑거 제작

    if (making[i - 1]['shape'] == 'up' or
        making[i - 1]['speed'] == 'fast') \
            and not i == 0:
        not_use = made_finger[-1]  # 만들때 못사용하는 핑거

    else:
        not_use = None

    current_len = len(making[i]['finger'])

    if l_r == 'right':
        made_finger = right_down_left_up(making, i, made_finger,
                                         current_len, not_use)
    elif l_r == 'left':
        made_finger = right_up_left_down(making, i, made_finger,
                                         current_len, not_use)

    return made_finger, i


def right_up_left_down(making, i, made_finger, current_len, not_use):
    """
    모두 처리후 오른손 기준으로 제작이 됬으므로 왼손이라면 반전을 시킨다.
    """

    # 현재 노트의 차이를 계산한다.
    difference = number_distance(making[i]['finger'])

    # end finger 를 정하는 과정,
    # 이때 end finger 는 현재 노트가 2개일때만 사용된다.

    # 개수가 1인 경우는 3, 4, 5의 배수를 돌리고 나머지가 1인 경우 밖에 없음
    if current_len == 1:

        if not_use == 4:
            made_finger += [1]

        else:
            made_finger += [4]

    elif current_len == 2:
        if not_use == 2:
            made_finger += [3, 4]

        elif not_use == 1:
            made_finger += [2, 3]

        # 2개 기본값
        else:
            if difference == 2:
                made_finger += [2, 3]

            # 135 패턴 유도
            if difference == 3 or difference == 4:
                made_finger += [1, 3]

            elif difference == 5:
                made_finger += [1, 5]

    # 길이가 3 혹은 3의 배수
    elif current_len == 3 or \
            (current_len >= 6 and current_len % 3 == 0
             and not making[i]['speed'] == 'fast'):
        if not_use == 2:
            for r in range(0, current_len // 3):
                made_finger += [1, 2, 3]

        else:
            for r in range(0, current_len // 3):
                made_finger += [2, 3, 4]

    # 길이가 4 혹은 4의 배수
    elif current_len == 4 or \
            (current_len >= 6 and current_len % 4 == 0
            and not making[i]['speed'] == 'fast'):
        if not_use == 1:
            for r in range(0, current_len // 4):
                made_finger += [2, 3, 4, 5]

        else:
            for r in range(0, current_len // 4):
                made_finger += [1, 2, 3, 4]

    # 길이가 5 (배수 x)
    elif current_len == 5:
        if making[i]['speed'] == 'fast':
            made_finger += [1, 2, 3, 4, 5]

        elif not_use == 1:
            for r in range(0, current_len // 4):
                made_finger += [2, 3, 4, 3, 4]
                # [4, 3, 2, 3, 2]

        else:
            for r in range(0, current_len // 4):
                made_finger += [1, 2, 3, 2, 3]
                # [3, 2, 1, 2, 1]

    # 3, 4, 5 의 배수 x, 6 이상의 노트들
    # 무한 루프해서 4개 핑거(1234) 로 채운다음 나머지로 마무리
    else:
        if making[i]['speed'] == 'fast':
            while True:
                if current_len <= 5:
                    remain = current_len
                    break

                if current_len == 6:
                    if not_use == 1:
                        made_finger += [2, 3, 4, 3, 2, 1]
                    else:
                        made_finger += [1, 2, 3, 4, 3, 2]
                    current_len -= 6

                elif current_len == 7:
                    if not_use == 1:
                        made_finger += [2, 3, 4, 3, 2, 1, 2]
                    else:
                        made_finger += [1, 2, 3, 4, 3, 2, 1]
                    current_len -= 7

                elif current_len >= 8:
                    if not_use == 1:
                        made_finger += [2, 3, 4, 5, 1]
                    else:
                        made_finger += [1, 2, 3, 4, 5]
                    current_len -= 5

        else:
            num_re = current_len // 4
            remain = current_len % 4
            if not_use == 1:
                for r in range(0, num_re):
                    made_finger += [2, 3, 4, 1]
            else:
                for r in range(0, num_re):
                    made_finger += [1, 2, 3, 4]

        if not remain == 0:
            not_use = made_finger[-1]  # 몇번 반복 했으므로 못쓰는 핑거를 재 설정
            made_finger = right_up_left_down(making, i, made_finger,
                                             remain, not_use)

    return made_finger


def right_down_left_up(making, i, made_finger, current_len, not_use):
    """
    모두 처리후 오른손 기준으로 제작이 됬으므로 왼손이라면 반전을 시킨다.
    """

    # 현재 노트의 차이를 계산한다.
    difference = number_distance(making[i]['finger'])

    # end finger 를 정하는 과정,
    # 이때 end finger 는 현재 노트가 2개일때만 사용된다.

    # 개수가 1인 경우는 3, 4, 5의 배수를 돌리고 나머지가 1인 경우 밖에 없음
    if current_len == 1:

        if not_use == 4:
            made_finger += [3]

        else:
            made_finger += [4]

    elif current_len == 2:
        if not_use == 3:
            made_finger += [2, 1]

        elif not_use == 4:
            if difference == 2 or difference == 3:
                made_finger += [3, 2]

            else:
                made_finger += [3, 1]

        # 그 전이 5로 끝났다는것, 31로 패턴 유지 [.. 5, 3, 1]
        elif not_use == 5:
            made_finger += [3, 1]

        # 2개 기본값
        else:
            if difference == 2:
                made_finger += [3, 2]

            # 135 패턴 유도
            elif difference == 3 or difference == 4:
                made_finger += [3, 1]

            elif difference == 5:
                made_finger += [5, 1]

    # 길이가 3 혹은 3의 배수
    elif current_len == 3 or \
            (current_len >= 6 and current_len % 3 == 0):
        if not_use == 4:
            for r in range(0, current_len // 3):
                made_finger += [3, 2, 1]

        else:
            for r in range(0, current_len // 3):
                made_finger += [4, 3, 2]

    # 길이가 4 혹은 4의 배수
    elif current_len == 4 or \
            (current_len >= 6 and current_len % 4 == 0):
        if not_use == 4:
            for r in range(0, current_len // 4):
                made_finger += [5, 4, 3, 2]

        else:
            for r in range(0, current_len // 4):
                made_finger += [4, 3, 2, 1]

    # 길이가 5 (배수 x)
    elif current_len == 5:
        if not_use == 4:
            for r in range(0, current_len // 4):
                made_finger += [3, 2, 1, 2, 1]

        else:
            for r in range(0, current_len // 4):
                made_finger += [4, 3, 2, 3, 2]

        # 3, 4, 5 의 배수 x, 7 이상의 노트들
        # 무한 루프해서 4개 핑거(1234) 로 채운다음 나머지로 마무리
    else:
        num_re = current_len // 4
        remain = current_len % 4

        if not_use == 4:
            for r in range(0, num_re):
                made_finger += [3, 2, 1, 4]
        else:
            for r in range(0, num_re):
                made_finger += [4, 3, 2, 1]

        not_use = made_finger[-1]
        made_finger = right_down_left_up(making, i, made_finger,
                                         remain, not_use)

    return made_finger


def multi(making, i, made_finger, l_r):
    # 다음 노트가 무엇인지 보고 끝 핑거를 정한 후 앞쪽 핑거 제작
    last_octave = 0  # 마지막으로 제작된 높은 옥타브
    o = 0  # ['finger'] 안을 도는 i 대체값

    # 다음 노트가 있는 경우
    while True:
        # 더이상 노트가 없는 경우
        if o >= len(making[i]['finger']):
            break

        # 다음 노트가 없는 경우
        elif o == len(making[i]['finger']) - 1:
            difference = number_distance(making[i]['finger'][o])
            made_finger = multi_make(making[i]['finger'], o, len(making[i]['finger'][o]),
                                     made_finger, last_octave, 1, 'up', difference, l_r)
            break

        # 적어도 하나의 노트가 있는 경우
        else:

            # 현재 멀티의 개수
            length_multi = len(making[i]['finger'][o])
            # 마지막으로 처리한 제일 높은 옥타브
            last_octave = making[i]['finger'][o][-1]

            o += 1
            length_multi_2 = len(making[i]['finger'][o])
            last_octave_2 = making[i]['finger'][o][-1]

            count = 1

            # 개수 최소 2개이상
            if length_multi == length_multi_2:
                count += 1
                o += 1
                direction = up_down(last_octave, last_octave_2)

                # 2개라면 거리를 잰다.
                if length_multi == 2:
                    difference = number_distance(making[i]['finger'][o - 1])

                else:
                    difference = 0

                # 같은 개수의 멀티가 얼마나 있는지 센다
                while True:
                    # 더이상 노트가 없는 경우
                    if o >= len(making[i]['finger']):
                        break

                    else:
                        length_multi_2 = len(making[i]['finger'][o])
                        last_octave_2 = making[i]['finger'][o][-1]

                        if length_multi == 2:
                            difference_2 = number_distance(making[i]['finger'][o])

                        else:
                            difference_2 = 0

                        direction_2 = up_down(last_octave, last_octave_2)

                        # 같은 개수, 방향의 멀티 계속 카운트
                        if length_multi == length_multi_2 and \
                                direction == direction_2 and \
                                difference == difference_2:
                            count += 1
                            o += 1

                        else:
                            o -= 1
                            break

            # 개수 1개
            else:
                # 위에서 +1 을 했으므로 다시 -1을 해준다
                o -= 1
                # last octave 재설정
                try:
                    last_octave = making[i]['finger'][o - 2][-1]

                except IndexError:
                    last_octave = making[i]['finger'][o - 1][-1]

                direction = 'none'
                if length_multi == 2:
                    difference = number_distance(making[i]['finger'][o])

                else:
                    difference = 0

            made_finger = multi_make(making[i]['finger'], o, length_multi, made_finger,
                                     last_octave, count, direction, difference, l_r)
            o += 1

    return made_finger


def multi_make(note_list, o, length, made_finger,
               last_octave, count, direction, difference, l_r):
    """

    :param note_list:
    :param o:
    :param length:
    :param made_finger:
    :param last_octave:
    :param count: 얼마나 같은 노트가 반복적으로 있는지에 대한 숫자, 후에 반복용으로 쓰임
    :param direction: 위 / 아래
    :param difference: 맨 앞, 뒤 노트의 차이
    :return:
    """
    # 23/34,   13/24,  14,  single
    if length == 2:
        # 23/34
        if difference == 2:
            if count == 1:
                current_octave = note_list[o - 1][-1]
                if last_octave < current_octave:
                    made_finger += [right_left([3, 4], l_r)]

                else:
                    made_finger += [[2, 3]]

            else:
                # 123 >> 234
                if direction == 'up':
                    made_finger = multi_make_2([right_left([2, 3], l_r)],
                                               [right_left([3, 4], l_r)],
                                               count, made_finger)

                elif direction == 'down':
                    made_finger = multi_make_2([right_left([3, 4], l_r)],
                                               [right_left([2, 3], l_r)],
                                               count, made_finger)

        # 13/24
        elif difference == 3:
            if count == 1:
                current_octave = note_list[o - 1][-1]
                if last_octave < current_octave:
                    made_finger += [right_left([2, 4], l_r)]

                else:
                    made_finger += [right_left([1, 3], l_r)]

            else:
                # 123 >> 234
                if direction == 'up':
                    made_finger = multi_make_2([right_left([1, 3], l_r)],
                                               [right_left([2, 4], l_r)],
                                               count, made_finger)

                elif direction == 'down':
                    made_finger = multi_make_2([right_left([2, 4], l_r)],
                                               [right_left([1, 3], l_r)],
                                               count, made_finger)

        elif difference == 4:
            for i in range(0, count):
                made_finger += [right_left([1, 4], l_r)]

            return made_finger

        # single 처리 후 up, down 처리
        elif difference == 5:
            for i in range(0, count):
                made_finger += [right_left([1, 5], l_r)]

            return made_finger

    # 123/234
    elif length == 3:
        if count == 1:
            current_octave = note_list[o - 1][-1]
            if last_octave < current_octave:
                made_finger += [right_left([2, 3, 4], l_r)]

            else:
                made_finger += [right_left([1, 2, 3], l_r)]

        else:
            # 123 >> 234
            if direction == 'up':
                made_finger = multi_make_2([right_left([1, 2, 3], l_r)],
                                           [right_left([2, 3, 4], l_r)],
                                           count, made_finger)

            elif direction == 'down':
                made_finger = multi_make_2([right_left([2, 3, 4], l_r)],
                                           [right_left([1, 2, 3], l_r)],
                                           count, made_finger)

    elif length == 4:
        for i in range(0, count):
            made_finger += [right_left([1, 2, 3, 4], l_r)]

    elif length == 5:
        for i in range(0, count):
            made_finger += [right_left([1, 2, 3, 4, 5], l_r)]

    return made_finger


def multi_make_2(add_finger_1, add_finger_2, count, made_finger):
    """
    주어진 2개의 멀티 핑거 (add_finger_1, add_finger_2) 를
    얼마나 반복시킬지, 어떻게 반복시킬지 정한다.
    """
    # 짝수 라면
    if count % 2 == 0:
        for i in range(0, count):
            made_finger += add_finger_1
            made_finger += add_finger_2

    # 홀수 라면
    else:
        for i in range(0, count - 1):
            made_finger += add_finger_1
            made_finger += add_finger_2
    made_finger += add_finger_2

    return made_finger


def one_make(making, i, made_finger, l_r):
    """ one 일때는 다음 혹은 이전 노트와의 연관성을 보고
    핑거를 만들어낸다. """
    # 기본적으로 다음 노트와 비교를한다.
    one = making[i]['finger'][0]

    try:
        compare = making[i + 1]

    # 만약 다음 노트가 없다면 이게 마지막이므로 이전 노트와 비교한다.
    except IndexError:
        compare = making[i - 1]

    # (전 / 다음 노트가) 멀티인 경우, 멀티의 좌우 끝쪽 노트를 비교대상으로 삼는다.
    if isinstance(compare['finger'][0], list):
        compare_1 = compare['finger'][0][0]
        compare_2 = compare['finger'][0][-1]

        # 멀티보다 작을 경우
        if compare_1 > one:
            if l_r == 'right':
                made_finger += [1]

            else:
                made_finger += [5]

        # 가운데에 위치하거나 같을 경우
        elif compare_1 <= one <= compare_2:
            made_finger += [3]

        # 멀티보다 클 경우
        elif compare_2 < one:
            if l_r == 'right':
                made_finger += [5]

            else:
                made_finger += [1]

    # (전 / 다음 노트가) 싱글인 경우
    else:
        compare = compare['finger'][-1]

        # 작을 경우
        if compare > one:
            before_finger = made_finger[-1] - 1
            # 그전 노트가 1이라서 -1 하면 0이 될경우
            if before_finger == 0:
                made_finger += [4]

            else:
                made_finger += [before_finger]

        # 가운데에 위치하거나 같을 경우
        elif compare == one:
            made_finger += [made_finger[-1]]

        # 클 경우
        elif compare < one:
            # 그전 노트가 5이라서 +1 하면 6이 될경우
            before_finger = made_finger[-1] + 1
            if before_finger == 6:
                made_finger += [1]

            else:
                made_finger += [before_finger]

    return made_finger


def same_make(making, i, made_finger, l_r):
    """ same 일때는 다음 혹은 이전 노트와의 연관성을 보고
        핑거를 만들어낸다. """

    insert_finger = []

    if making[i]['speed'] == 'fast':
        if making[i - 1]['speed'] == 'fast' \
                and not i == 0:
            not_use = made_finger[-1]  # 만들때 못사용하는 핑거

        else:
            not_use = None

        current_len = len(making[i]['finger'])

        if l_r == 'right':
            made_finger = right_up_left_down(making, i, made_finger,
                                             current_len, not_use)
        elif l_r == 'left':
            made_finger = right_down_left_up(making, i, made_finger,
                                             current_len, not_use)

    else:
        # 기본적으로 다음 노트와 비교를한다.
        same = making[i]['finger'][0]

        try:
            compare = making[i - 1]

        # 만약 다음 노트가 없다면 이게 마지막이므로 이전 노트와 비교한다.
        except IndexError:
            compare = making[i + 1]

        # (전 / 다음 노트가) 멀티인 경우, 멀티의 좌우 끝쪽 노트를 비교대상으로 삼는다.
        if isinstance(compare['finger'][0], list):
            compare_1 = compare['finger'][0][0]
            compare_2 = compare['finger'][0][-1]

            # 멀티보다 작을 경우
            if compare_1 > same:
                if l_r == 'right':
                    insert_finger.append(1)

                else:
                    insert_finger.append(5)

            # 가운데에 위치하거나 같을 경우
            elif compare_1 <= same <= compare_2:
                insert_finger.append(3)

            # 멀티보다 클 경우
            elif compare_2 < same:
                if l_r == 'right':
                    insert_finger.append(5)

                else:
                    insert_finger.append(1)

        # (전 / 다음 노트가) 싱글인 경우
        else:
            compare = compare['finger'][-1]

            # 작을 경우
            if compare > same:
                before_finger = made_finger[-1] - 1
                # 그전 노트가 1이라서 -1 하면 0이 될경우
                if before_finger == 0:
                    insert_finger.append(4)

                else:
                    insert_finger.append(before_finger)

            # 가운데에 위치하거나 같을 경우
            elif compare == same:
                insert_finger.append(made_finger[-1])

            # 클 경우
            elif compare < same:
                # 그전 노트가 5이라서 +1 하면 6이 될경우
                before_finger = made_finger[-1] + 1
                if before_finger == 6:
                    insert_finger.append(1)

                else:
                    insert_finger.append(before_finger)

    # 들어있는 핑거 수만큼 반복
    for h in range(0, len(making[i]['finger'])):
        made_finger += insert_finger

    return made_finger


def two_two_make(making, i, made_finger, l_r):
    """
    2 >> 2 의 과정 처리는 아래와 같다. (완전 같은 경우 / 완전 다른 경우 제외)

    1. 얼마나 같은 형태를 유지하는 노트가 있는지 combine_note 로 묶는다.

    2. new_making 으로 핑거를 만들 준비를 한다.

    3. new_making 의 정보로 insert_later 리스트를 다시 만든다.

    3. insert_later 으로 만든 핑거 리스트에 1 혹은 4를 중간 중간에 결합 시킴
    ex) [4, 3, 2] >> [1, 4, 1, 3, 1, 2]

    """
    s_d = 'none'

    try:
        current_note = making[i]
        next_note = making[i + 1]

    except IndexError:
        made_finger, i = up(making, i, made_finger, l_r)

        return made_finger, i

    # up (2개) >> up (2개)
    if next_note['shape'] == 'up' \
            and len(current_note['finger']) == 2 \
            and len(next_note['finger']) == 2:
        current_note = current_note['finger']
        next_note = next_note['finger']

        # 왼쪽만 같은 경우
        # 바로 1을 넣고  반복
        if current_note[0] == next_note[0]:
            inside_later = []
            count = 2  # 이미 2개까진 확인 했으므로
            compare_val = current_note[0]  # 계속 왼쪽이 같은지 확인해야 하므로
            # compare_val 로 하는 이유는 같은 쪽(current_note[0])의 값이 다르다면 나눠야 하기 떄문

            combine_shape = {'octave': [current_note[1], next_note[1]],
                             'next': 'new', 'speed': making[i]['speed']}

            # 반복해서 얼마나 2 >> 2 형태가 있는지 확인 후
            # combine_shape 에 합친다.
            while True:
                i += 1
                current_note = next_note

                # 다음 노트가 있는지 확인
                try:
                    next_note = making[i + 1]['finger']
                # 없다면 반복 종료
                except IndexError:
                    break
                # 합칠 수 있는 형태라면
                if compare_val == next_note[0] and \
                        current_note[1] != next_note[1]:
                    count += 1
                    combine_shape['octave'] += [next_note[1]]

                else:
                    break

            # combine_shape 가 완성됬다면 아래 함수로 어떤 형태(up, down)의 노트가 되었는지
            # 확인 할 수 있는 사전(dic) 형태로 바꾼다. 이걸로 형태와 개수를 통해 아래에서
            # ex) new_making = {

            # inside_later 의 리스트를 완성할 수 있으며, 사이사이에 1 혹은 4를 반복 시킨다.
            # ex) inside_later == [4, 3, 2] >> [1, 4, 1, 3, 1, 2]
            new_making, none = finger_combine([combine_shape], 0, l_r)

            len_made = 0
            while True:
                if len_made >= len(new_making):
                    break

                if new_making[len_made]['shape'] == 'up':
                    len_f = len(new_making[len_made]['finger'])

                    # 오른손은 1 (옥타브 기준 왼쪽) 반복이므로 left_same... 을 쓴다.
                    if l_r == 'right':
                        inside_later = left_same_right_up_left_down(inside_later, len_f)

                    # 왼손이라면 4 (옥타브 기준 오른쪽) 반복 되야 하므로
                    # right_same 을 쓴다.
                    elif l_r == 'left':
                        inside_later = right_same_right_down_left_up(inside_later, len_f)
                    len_made += 1

                elif new_making[len_made]['shape'] == 'down':
                    len_f = len(new_making[len_made]['finger'])

                    if l_r == 'right':
                        inside_later = left_same_right_down_left_up(inside_later, len_f)

                    elif l_r == 'left':
                        inside_later = right_same_right_up_left_down(inside_later, len_f)
                    len_made += 1

                # one, same 등은 존재 할 수 없다. 바뀌는 쪽은 계속 옥타브가 바뀌어야 하기 때문

            # [4, 3, 2] >> [1, 4, 1, 3, 1, 2]
            if new_making[len_made]['shape'] == 'up':

                # 짝수 (먼저 들어가서 반복)
                # 오른손 == 1 반복
                if l_r == 'right':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert(in_1 * 2, 1)
                # 왼손 이니 4 반복
                elif l_r == 'left':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert(in_1 * 2, 4)

            else:
                # 홀수 (한칸 뒤로 들어가서 반복)
                if l_r == 'right':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert((in_1 * 2) + 1, 1)
                elif l_r == 'left':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert((in_1 * 2) + 1, 4)

            made_finger.extend(inside_later)
            i += 1

        # 오른쪽만 같은 경우
        elif current_note[1] == next_note[1]:
            inside_later = []
            count = 2
            compare_val = current_note[1]
            # compare_val 로 하는 이유는 같은 쪽(current_note[0])의 같이 다르다면 나눠야 하기 떄문

            combine_shape = {'octave': [current_note[0], next_note[0]],
                             'next': 'new', 'speed': making[i]['speed']}
            while True:
                i += 1
                current_note = next_note

                try:
                    next_note = making[i + 1]['finger']

                except IndexError:
                    break

                if compare_val == next_note[1] and \
                        current_note[0] != next_note[0]:
                    count += 1
                    combine_shape['octave'] += [next_note[0]]

                else:
                    break

            new_making, none = finger_combine([combine_shape], 0, l_r)

            len_made = 0
            while True:
                if len_made >= len(new_making):
                    break

                if new_making[len_made]['shape'] == 'up':
                    len_f = len(new_making[len_made]['finger'])

                    # 오른손은 4 반복이므로 right_same... 을 쓴다.
                    if l_r == 'right':
                        inside_later = right_same_right_up_left_down(inside_later, len_f)

                    # 왼손이라면 1이 반복 되야 하므로
                    # left_same 을 쓴다.
                    elif l_r == 'left':
                        inside_later = left_same_right_down_left_up(inside_later, len_f)
                    len_made += 1

                elif new_making[len_made]['shape'] == 'down':
                    len_f = len(new_making[len_made]['finger'])

                    if l_r == 'right':
                        inside_later = right_same_right_down_left_up(inside_later, len_f)

                    elif l_r == 'left':
                        inside_later = left_same_right_up_left_down(inside_later, len_f)
                    len_made += 1

                elif new_making[len_made]['shape'] == 'one':
                    len_f = len(new_making[len_made]['finger'])
                    if l_r == 'right':
                        inside_later = right_same_right_down_left_up(inside_later, len_f)

                    elif l_r == 'left':
                        inside_later = left_same_right_down_left_up(inside_later, len_f)
                    len_made += 1

            # 현재 right same 상태이다.
            # 오른손 이고 up 형태라면 / 왼손 이고 down 형태이면
            if new_making[0]['shape'] == 'up':

                # 홀수 (한칸 뒤로 들어가서 반복)
                if l_r == 'right':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert((in_1 * 2) + 1, 4)
                elif l_r == 'left':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert((in_1 * 2) + 1, 1)

            else:
                # 짝수 (먼저 들어가서 반복)
                if l_r == 'right':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert(in_1 * 2, 4)
                elif l_r == 'left':
                    for in_1 in range(0, len(inside_later)):
                        inside_later.insert(in_1 * 2, 1)

            made_finger.extend(inside_later)
            i += 1

        # 완전 같은 경우 / 완전 다른 경우
        else:
            if current_note == next_note:
                s_d = 'same'
            elif current_note[0] != next_note[0] and \
                    current_note[1] != next_note[1]:
                s_d = 'different'

            count = 2
            while True:
                i += 1
                current_note = next_note

                # 다음 노트가 있는지 확인
                try:
                    next_note = making[i + 1]['finger']
                # 없다면 반복 종료
                except IndexError:
                    break

                # 완전 같은 경우 / 완전 다른 경우
                if (s_d == 'same' and current_note == next_note) or \
                        (s_d == 'different' and
                         current_note[0] != next_note[0] and
                         current_note[1] != next_note[1]):
                    count += 1

                else:
                    break

            repeat_finger, i = up(making, i, made_finger, l_r)

            for g in range(0, count):
                made_finger += repeat_finger

    # 아무것도 아닌 경우
    else:
        made_finger, i = up(making, i, made_finger, l_r)
        i += 1

    return made_finger, i


def left_same_right_up_left_down(made_finger, current_len):
    """
        모두 처리후 오른손 기준으로 제작이 됬으므로 왼손이라면 반전을 시킨다.
        """

    # 현재 노트의 차이를 계산한다.

    # end finger 를 정하는 과정,
    # 이때 end finger 는 현재 노트가 2개일때만 사용된다.

    # 개수가 1인 경우는 3, 4, 5의 배수를 돌리고 나머지가 1인 경우 밖에 없음
    if current_len == 1:
        made_finger += [3]

    elif current_len == 2:
        made_finger += [3, 4]

    # 길이가 3 혹은 3의 배수
    elif current_len >= 3:
        num_re = current_len // 3
        remain = current_len % 3
        for i in range(0, num_re):
            made_finger += [2, 3, 4]

        made_finger = left_same_right_up_left_down(made_finger, remain)

        # 3, 4, 5 의 배수 x, 7 이상의 노트들
        # 무한 루프해서 4개 핑거(1234) 로 채운다음 나머지로 마무리

    return made_finger


def left_same_right_down_left_up(made_finger, current_len):
    """
        모두 처리후 오른손 기준으로 제작이 됬으므로 왼손이라면 반전을 시킨다.
        """

    # 개수가 1인 경우는 3, 4, 5의 배수를 돌리고 나머지가 1인 경우 밖에 없음
    if current_len == 1:
        made_finger += [4]

    elif current_len == 2:
        made_finger += [3, 2]

    # 길이가 3 혹은 3의 배수
    elif current_len >= 3:
        num_re = current_len // 3
        remain = current_len % 3
        for i in range(0, num_re):
            made_finger += [4, 3, 2]

        made_finger = left_same_right_down_left_up(made_finger, remain)

        # 3, 4, 5 의 배수 x, 7 이상의 노트들
        # 무한 루프해서 4개 핑거(1234) 로 채운다음 나머지로 마무리
    return made_finger


def right_same_right_up_left_down(made_finger, current_len):
    """
        모두 처리후 오른손 기준으로 제작이 됬으므로 왼손이라면 반전을 시킨다.
        """

    # 현재 노트의 차이를 계산한다.

    # end finger 를 정하는 과정,
    # 이때 end finger 는 현재 노트가 2개일때만 사용된다.

    # 개수가 1인 경우는 3, 4, 5의 배수를 돌리고 나머지가 1인 경우 밖에 없음
    if current_len == 1:
        made_finger += [1]

    elif current_len == 2:
        made_finger += [2, 3]

    # 길이가 3 혹은 3의 배수
    elif current_len >= 3:
        num_re = current_len // 3
        remain = current_len % 3
        for i in range(0, num_re):
            made_finger += [1, 2, 3]

        made_finger = right_same_right_up_left_down(made_finger, remain)

        # 3, 4, 5 의 배수 x, 7 이상의 노트들
        # 무한 루프해서 4개 핑거(1234) 로 채운다음 나머지로 마무리

    return made_finger


def right_same_right_down_left_up(made_finger, current_len):
    """
        모두 처리후 오른손 기준으로 제작이 됬으므로 왼손이라면 반전을 시킨다.
        """

    # 현재 노트의 차이를 계산한다.

    # end finger 를 정하는 과정,
    # 이때 end finger 는 현재 노트가 2개일때만 사용된다.

    # 개수가 1인 경우는 3, 4, 5의 배수를 돌리고 나머지가 1인 경우 밖에 없음
    if current_len == 1:
        made_finger += [3]

    elif current_len == 2:
        made_finger += [3, 2]

    # 길이가 3 혹은 3의 배수
    elif current_len >= 3:
        num_re = current_len // 3
        remain = current_len % 3
        for i in range(0, num_re):
            made_finger += [3, 2, 1]

        made_finger = right_same_right_down_left_up(made_finger, remain)

        # 3, 4, 5 의 배수 x, 7 이상의 노트들
        # 무한 루프해서 4개 핑거(1234) 로 채운다음 나머지로 마무리
    return made_finger


def finger_combine(finger_list, i, hand):
    """

    up, down, multi, one, same 구분

    속도 관련 : slow 기준점이 넘어가는 것은 합치되, 기준점 부터는 같은 것 이외에 합치지 않는다.

    hand 구별 이유 :  last_multi 살려둘것인가의 여부 right : 살림 / left : 단일화 처리


    """
    combine_finger = []
    o = 0  # 무한반복 i 대체값
    making = []

    if finger_list[i]['next'] == 'end':
        speed = 'slow'
    else:
        speed = finger_list[i]['speed']

    while True:
        # 리스트 다 돌았다면 종료
        if o >= len(finger_list[i]['octave']):
            break

        # single 노트 묶음 (up, down, one, same...)
        number_1 = take_out(finger_list, i, o, speed, hand)
        o += 1

        number_2 = take_out(finger_list, i, o, speed, hand)

        direction = up_down_one_same(number_1, number_2)

        # multi 무한루프
        if direction == 'multi':
            combine_finger.append(number_1)

            if number_2 != 'none':
                combine_finger.append(number_2)

            while True:
                number_1 = number_2
                o += 1

                number_2 = take_out(finger_list, i, o, speed, hand)

                direction_2 = up_down_one_same(number_1, number_2)

                if direction == direction_2:
                    combine_finger.append(number_2)

                else:
                    break

        elif direction == 'last_multi':
            combine_finger.append(number_1)

        # one 제외 무한루프 (same 까지 포함)
        elif not direction == 'one':
            combine_finger.append(number_1)
            combine_finger.append(number_2)
            while True:
                number_1 = number_2
                o += 1

                number_2 = take_out(finger_list, i, o, speed, hand)

                direction_2 = up_down_one_same(number_1, number_2)

                if direction == direction_2:
                    combine_finger.append(number_2)

                else:
                    break

        # one 이라면
        else:
            combine_finger.append(number_1)

        making.append(
            {
                'finger': combine_finger,
                'shape': direction,
                'speed': speed
            }
        )

        combine_finger = []

    return making, i


def take_out(finger_list, i, o, speed, hand):
    """ 스피드를 보고 멀티라면 단일로 바꾸는 등 변화를 준다. """
    try:
        number = finger_list[i]['octave'][o]

    except IndexError:
        number = 'none'
        return number

    try:
        number_2 = finger_list[i]['octave'][o + 1]

    except IndexError:
        number_2 = 'none'

    # 멀티 허용 (속도 : slow)
    if speed == 'slow' and isinstance(number, list):
        number = finger_list[i]['octave'][o]

    # fast 가 아닐때 아래 구문을 실행시킨다
    # 마지막 멀티일때 (medium 일때는 미적용)
    # 연타 허용 (fast 이전까지)
    elif not speed == 'fast' and \
            (isinstance(number, list) and number_2 == 'none' and not speed == 'medium') or \
            (isinstance(number, list) and number == number_2):
        number = finger_list[i]['octave'][o]

    # 나머지는 싱글 처리
    else:
        # 멀티라면 (높은 옥타브의 노트만 사용)
        if isinstance(number, list):
            number = number[-1]

    return number


def up_down_one_same(number_1, number_2):
    if isinstance(number_1, list):
        if number_2 == 'none':
            return 'last_multi'

        else:
            return 'multi'

    elif number_2 == 'none' or isinstance(number_2, list):
        return 'one'

    # 여기서 부터는 숫자비교
    elif number_1 < number_2:
        return 'up'

    elif number_1 > number_2:
        return 'down'

    elif number_1 == number_2:
        return 'same'