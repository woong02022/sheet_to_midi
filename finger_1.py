scan_list = []  # main 에서 스캔으로 만든 리스트

# 나중에는 bpm 으로 자동 계산 후 만들어져야 한다.

slow = 1  # 4분음표
benchmark = 0.33  # 8분음표 3연음 (기준점)
# (slow < 속도 <= 기준점  : 중간, 기준점 < 속도: 빠름)

i = 0

combine_list = []
finger_make_list = []


def what_speed(speed):
    # slow
    if speed >= slow:
        return 'slow'

    # middle
    elif benchmark < speed < slow:
        return 'medium'

    # fast
    elif speed <= benchmark:
        return 'fast'


def what_shape(octave, compare_octave,
               speed, compare_speed):
    """ 먼저 스피드를 비교해 서로 합칠 수 있는지 먼저 판단 후
    만약 합칠 수 없다면 느려서 다시 시작해야 하는지도 아닌지도 판단.
    한개의 노트가 멀티인지 싱글인지
    싱글이라면 첫 노트와 비교해서 어떤 노트인지 알아낸다 """

    if speed != compare_speed:
        if speed == 'slow':
            # 느림 이하 므로 합치는거 자체를 다시 한다
            return 'restart'
        else:
            # 단순 중간 이상 스피드지만 스피드가 달라 못하침
            return 'cant_combine'

    elif isinstance(octave, list):
        return 'multi'

    else:
        if octave > compare_octave:
            return 'up'

        elif octave < compare_octave:
            return 'down'


def overall_shape(octave_1, octave_2):
    """ 처음 2개의 옥타브를 비교하고 합쳐야할 모양의 이름을 보낸다 """

    if isinstance(octave_1, list):
        return 'multi'

    elif not isinstance(octave_1, list) and \
            isinstance(octave_2, list):
        return 'one_multi'  # multi one 모양은 없다

    else:
        if octave_1 < octave_2:
            return 'up'

        elif octave_1 > octave_2:
            return 'down'

        elif octave_1 == octave_2:
            return 'same'


def confirm_speed(current_speed, compare_speed):
    speed = what_speed(current_speed)

    if compare_speed == speed:
        return 'true'

    else:
        if speed == 'slow':
            return 'new'

        else:
            return 'keep'


def prepare_make_finger(scan_list):
    # 현재 노트가 중간(4분음표) (jump 의 기준점이므로 나중에 변수로 바꿔야한다.)
    # 중간 이상 일때
    # 최소 다음 노트와 1개는 결합되어야 한다 (one 제외)

    # 이쪽 구간의 첫번째 노트의 스피드는 middle, fast 지만
    # 마지막으로 들어오는 노트의 스피드는 slow 이다.
    """
    그 전 노트가 첫번째 노트의 속도를 선택한다는 것을 잊지 마라 
    """
    i = 0

    finger_make_list = []

    # 처음 나오는 모든 쉼표들은 건너뛴다.
    while True:
        if scan_list[i]['shape'] == 'rest':
            i += 1

        else:
            break

    while True:
        if i >= len(scan_list):
            break

        else:
            # compare_speed = slow, medium, fast
            # 계속해서 speed 를 비교해서 최종적으로 합쳐지는 리스트중 제일 빠른 속도로 리스트를 설정한다.
            compare_speed = what_speed(scan_list[i]['note_number'])
            speed_val = scan_list[i]['note_number']
            new_list = {
                'octave': [scan_list[i]['octave']],
            }

        # 마지막 노트라면
        if i == len(scan_list) - 1:
            new_list['next'] = 'end'
            finger_make_list.append(new_list)
            break

        # 마지막 노트를 벗어난 상태
        elif i > len(scan_list) - 1:
            break

        else:

            while True:
                i += 1
                # 마지막 노트라면
                if i == len(scan_list):
                    new_list['next'] = 'new'
                    new_list['speed'] = compare_speed
                    break

                current_speed = what_speed(scan_list[i]['note_number'])

                # 계속해서 speed 를 비교해서 최종적으로 합쳐지는 리스트중 제일 빠른 속도로 리스트를 설정한다.
                if (compare_speed == 'medium' and current_speed == 'fast') or \
                        (compare_speed == 'fast' and current_speed == 'medium'):
                    compare_speed = current_speed

                current_octave = scan_list[i]['octave']
                speed_val_2 = scan_list[i]['note_number']

                # slow 라면 서로 속도가 같거나 빨라지는것 이외에 합칠 수 없다.
                if compare_speed == 'slow' and current_speed == 'slow' and \
                        speed_val >= speed_val_2:
                    new_list['octave'].append(current_octave)
                    speed_val = speed_val_2

                # medium, fast 라면 다음이 slow 가 아닌 이상 계속 합칠 수 있다.
                elif (compare_speed == 'medium' or compare_speed == 'fast') and not \
                        current_speed == 'slow':
                    new_list['octave'].append(current_octave)
                    speed_val = speed_val_2

                # slow 인데 다음이 빨라서 혹은 속도가 같이 않아서 끊기거나,
                # medium, fast 인데 다음이 slow 라서 끊기는 경우
                else:
                    # slow 인데 다음이 medium, fast 라서 끊기는 경우
                    if compare_speed == 'slow' and not current_speed == 'slow':
                        new_list['next'] = 'new'
                        new_list['speed'] = compare_speed
                        break

                    # slow 인데 다음이 더 느린 속도의 slow 라서 끊기는 경우
                    elif compare_speed == 'slow' and current_speed == 'slow':
                        new_list['octave'].append(current_octave)
                        new_list['next'] = 'new'
                        new_list['speed'] = compare_speed
                        i += 1
                        break

                    # medium, fast 인데 다음이 slow 라서 끊기는 경우
                    else:
                        new_list['octave'].append(current_octave)
                        new_list['next'] = 'new'
                        new_list['speed'] = compare_speed
                        i += 1
                        break

            finger_make_list.append(new_list)

    return finger_make_list
