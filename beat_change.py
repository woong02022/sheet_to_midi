def accept_beat(result):
    """
    triplet, dot 등
    octave 에 영향을 끼치는 것들을 모두 노트에 적용 시킨다.
    """
    i = 0  # result 반복자

    while True:

        if i >= len(result):
            break

        shape = result[i]['shape']

        if shape == 'triplet':
            accept_triplet(result, i)

        elif shape == 'dot':
            pass

    return result


def find_left_note(result, i):
    """
    현재 i값 위치에서 바로 다음에 있는
    노트를 인덱스에서 찿는다.
    그 인덱스값 (i) 를 반납

    """
    while True:
        i -= 1

        if i < 0:
            i = 'none'
            break

        if result[i]['shape'] == 'note' \
                and result[i]['note_number'] != 0:
            break

        else:
            continue

    return i


def find_right_note(result, i):
    """
    현재 i값 위치에서 바로 오른쪽에 있는
    노트를 인덱스에서 찿는다.
    그 인덱스값 (i) 를 반납

    """
    while True:
        i += 1

        if i > len(result):
            i = 'none'
            break

        if result[i]['shape'] == 'note' \
                and result[i]['note_number'] != 0:
            break

        else:
            continue

    return i


def accept_triplet(result, i):

    # 멀티부분은 건너 뛰었다. (note_number == 0)
    left_note_i = find_left_note(result, i)
    right_note_i = find_right_note(result, i)

    triplet_w = result[i]['coordinate'][0]
    left_w = result[left_note_i]['coordinate'][0]
    right_w = result[right_note_i]['coordinate'][0]

    left_distance = abs(triplet_w - left_w)
    right_distacne = abs(triplet_w - right_w)

    # triplet 이 왼쪽 노트와 더 가까울 경우
    # 왼쪽의 왼쪽 노트까지 적용 범위 이므로 아래와 같이 구한다.
    if left_distance < right_distacne:
        another_note = \
            find_left_note(result, left_note_i)
    # 아니라면 오른쪽의 오른쪽 노트 까지 구한다.
    else:
        another_note = \
            find_right_note(result, right_note_i)


def find_note_number(result, i, name):
    """
           (파이썬에서는 4분음표 == 1 ,
           8분음표 == 0.5 로 (곱할 값)을 알려준다
   )


        점 온음표 = 0.1875

           온음표 = 0.25

        점 2분음표 = 0.375

           2분음표 = 0.5

        점 4분음표 = 0.75

           4분음표 = 1

        점 8분음표 = 1.5

           8분음표 = 2

        점 16분음표 == 3

           16분음표 = 4 """

    m = -1
    change_name = False

    note_change = 0

    # 2. (3연음, dot 등) note_number 를 바꿀 요소가 있는지 검색
    while True:
        # 정수이거나 (?잇단음표), 나머지 'dot' 등의 기호가 있다면
        if isinstance(result[i][m], int) is True or \
                result[i][m] == 'dot':
            # note_change 가 얼마나
            note_change += 1
            m -= 1

        else:
            break

    # 음표를 숫자로 변환
    # 이때 m - note_change 값은 4분음표 일 경우 '8th' '16th' 등이 나온다.
    note_number = make_note_number(result, i, m, name)
    # note_index = note 딕셔너리 에서 현재 note_number 가 ?번째 index(list[?]) 인지
    note_index = list(note.values()).index(note_number)

    # note_number 재계산 (triplet, dot)
    if note_change != 0:
        for k in range(1, note_change + 1):
            note_number = re_note_number(note_number,
                                         result[i][m + k])

        m = -note_change - 1

    # quarter 즉 4분음표 가 아니면 '8th' 등이 존재 하지 않으므로
    # m에서 +1 해준다 (+1 하는 이유는 slur, dot 등은 존재할 수 있기 때문)
    #
    if not result[i][0][2].find('quarter_note') >= 0:
        m += 1

    if change_name is True:
        name = 'rest'

    return note_number, name, m
