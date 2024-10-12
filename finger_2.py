from shape import *


def up_down_same(combine_finger, i):
    # up
    if combine_finger[i] - combine_finger[i - 1] > 0:
        return 'up'
    # down
    elif combine_finger[i] - combine_finger[i - 1] < 0:
        return 'down'
    # same
    elif combine_finger[i] - combine_finger[i - 1] < 0:
        return 'same'


def make(finger_list, final_list, hand):
    i = 0

    # final_list 반복 용
    i_2 = 0
    made_finger = []

    while True:
        if i >= len(finger_list):
            break

        else:
            making, i = finger_combine(finger_list, i, hand)
            # 이제 여기에 스피드, 난이도 정보를 더 기입해 최종적으로 핑거링을 만든다.

            # 패턴 감지, 핑거 제작
            o = 0  # making 반복용
            while True:
                if o >= len(making):
                    break
                else:
                    made_finger, o = pattern_detect(making, o, made_finger, hand)
                    g = 0

                    while True:
                        if g == len(made_finger):
                            break
                        # 쉼표는 건너뛴다.
                        if final_list[i_2]['shape'] == 'rest':
                            i_2 += 1
                            continue

                        else:
                            final_list[i_2]['finger'] = made_finger[g]
                            i_2 += 1
                            g += 1

                    made_finger = []
                    o += 1
            i += 1

    return final_list


def pattern_detect(making, i, made_finger, l_r):
    # 패턴 최소 조건 == making 안이 2개 이상이여야함

    while True:
        if i >= len(making):
            break

        if making[i]['shape'] == 'up':
            try:
                current_note = making[i]
                next_note = making[i + 1]

            except IndexError:
                made_finger, i = up(making, i, made_finger, l_r)
                break

            # up (2개) >> up (2개) (이 패턴은 오른손만)
            # 오른손 제외하면 그냥 반복 처리
            else:

                # up (2개) >> up (2개)
                if next_note['shape'] == 'up' \
                        and len(current_note['finger']) == 2 \
                        and len(next_note['finger']) == 2:
                    made_finger, i = two_two_make(making, i, made_finger, l_r)
                    # i += 1 ..?
                # 아무것도 아닌 경우
                else:
                    made_finger, i = up(making, i, made_finger, l_r)
                    i += 1

        elif making[i]['shape'] == 'down':
            try:
                current_note = making[i]
                next_note = making[i + 1]

            except IndexError:
                made_finger, i = down(making, i, made_finger, l_r)
                break

            else:

                if next_note['shape'] == 'down' \
                        and len(current_note['finger']) == 2 \
                        and len(next_note['finger']) == 2:
                    made_finger, i = down(making, i, made_finger, l_r)
                    i += 1

                else:
                    made_finger, i = down(making, i, made_finger, l_r)
                    i += 1

        elif making[i]['shape'] == 'multi' or \
                making[i]['shape'] == 'last_multi':
            made_finger = multi(making, i, made_finger, l_r)
            i += 1

        elif making[i]['shape'] == 'one':
            made_finger = one_make(making, i, made_finger, l_r)
            i += 1

        elif making[i]['shape'] == 'same':
            made_finger = same_make(making, i, made_finger, l_r)
            i += 1

    return made_finger, i
