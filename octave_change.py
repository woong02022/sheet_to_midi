import copy

octave_list = {
    'a0': 21, 'b0': 23,
    'c1': 24, 'd1': 26, 'e1': 28, 'f1': 29, 'g1': 31, 'a1': 33, 'b1': 35,
    'c2': 36, 'd2': 38, 'e2': 40, 'f2': 41, 'g2': 43, 'a2': 45, 'b2': 47,
    'c3': 48, 'd3': 50, 'e3': 52, 'f3': 53, 'g3': 55, 'a3': 57, 'b3': 59,
    'c4': 60, 'd4': 62, 'e4': 64, 'f4': 65, 'g4': 67, 'a4': 69, 'b4': 71,
    'c5': 72, 'd5': 74, 'e5': 76, 'f5': 77, 'g5': 79, 'a5': 81, 'b5': 83,
    'c6': 84, 'd6': 86, 'e6': 88, 'f6': 89, 'g6': 91, 'a6': 93, 'b6': 95,
    'c7': 96, 'd7': 98, 'e7': 100, 'f7': 101, 'g7': 103, 'a7': 105, 'b7': 107,
    'c8': 108
}

deverse_octave_list = {v:k for k,v in octave_list.items()}

def accept_octave(result):
    """
    key_signature , flat, sharp, 8va/8vb 등
    octave 에 영향을 끼치는 것들을 모두 노트에 적용 시킨다.
    """
    i = 0  # result 반복자
    key_find = True

    # 임시표 리스트
    accidental_dic = {
        'sharp': [],
        'flat': [],
        'natural': []
    }
    # 조표 리스트
    key_signature_dic = {
        'sharp': [],
        'flat': [],
        'natural': []
    }
    while True:

        # 리스트 범위를 초과한 경우 >> 반복 종료
        if i >= len(result):
            break

        shape = result[i]['shape']

        # clef (음자리표) 설정 후 key 비교 리스트 제작에 써먹는다
        if shape == 'treble_clef' or \
                shape == 'bass_clef':
            clef = shape

        # bar(세로줄) 발견시
        # 다음 임시표 발견 시 조표 탐색으로 넘어가야 하므로
        # 아래 key_find 를 True 로 바꿔준다
        # 또한 임시표의 효력이 전부 사라지므로 아래와 같이 빈 사전으로 만든다.
        if shape == 'bar':
            key_find = True
            accidental_dic = {
                'sharp': [],
                'flat': [],
                'natural': []
            }

        # 임시표 발견 시
        elif shape == 'sharp' or \
                shape == 'flat' or \
                shape == 'natural':
            # 그전에 bar 발견 해서 조표 탐색으로 갈시
            # 조표 적용
            if key_find is True:
                key_signature_dic, accidental_dic, i = \
                    make_key_signature(result, i, shape,
                                       accidental_dic, clef, key_signature_dic)
                key_find = False

            # 임시표 적용
            else:
                accidental_dic, i = \
                    general_accidental(result, i, shape, accidental_dic, key_signature_dic)

        # 노트 발견 시 적용 시작
        elif shape == 'note':
            # bar가 등장했어도 노트가 먼저 나와버린 경우 조표가 아니므로
            key_find = False

            # 노트 옥타브 이름 리스트 생성
            # 이때 i값은 변경을 안하는데 나중에 적용시
            # 멀티인 경우 처음부터 적용해야 하기 때문
            note_octave_name_list = make_octave_name_list(result, i)

            # 이 정보를 바탕으로 적용을 해준다
            result, i = accept_all(result, i, note_octave_name_list,
                       key_signature_dic, accidental_dic)

        # 아무것도 아닌 경우 그냥 넘어간다
        i += 1

    return result


def make_key_signature(result, first_i, shape,
                       accidental_dic, clef, key_signature_dic):
    """

    현재 음계가 조표 리스트와 순서에 비교해서 맞는지 확인

    (맞다면) 조표 리스트에 추가
    (아니라면) - 일반 올림, 내림표로 쓰이는 임시표인지 확인
                확인 방법은 미리 만들어둔 노트 옥타브 리스트와 비교

                (맞다면) 임시표로 넣고 조표 탐색 중지
                (아니라면) 오류로 넣어진 임시표이므로 무시하고 다음 조표 탐색
    """
    # 만들어낼 조표 리스트
    i = copy.deepcopy(first_i)

    s = 0  # 현재 조표 확인으로서 몇번째 검사인지 확인용
    # 조표 순서가 있으므로 위의 s가 활용됨
    # ex) key_name = ['f', 'c', 'g', 'd', 'a', 'e', 'b']

    key_list = []
    key_num_list = []
    # 조표 검사할 리스트 미리 만들어두고
    key, key_name = key_signature(shape, clef, key_signature_dic)

    # 일반 올림표, 내림표로 쓰일지도 모르니까 다음 노트 리스트 만듬
    # 먼저 다음 노트 인덱스 값 알아내고
    next_note_i = next_note(result, i)

    if next_note_i == 'none':
        return key_signature_dic, accidental_dic, i

    # 옥타브 리스트도 얻어낸다
    note_octave_list = make_octave_list(result, next_note_i)

    next_i = i

    while True:
        # 다음 비교할것이 없다면
        # 반복 종료
        if next_i == 'none':
            break

        else:
            i = next_i

        # 현재 임시표의 옥타브 값
        current_octave = result[i]['octave']
        # 현재 음계가 조표 리스트와 순서에 비교해서 맞는지 확인
        # 맞다면 s(조표 비교 순서 반복자) 를 +1 해주고
        # 다음 비교로 간다
        # 인덱스 에러를 방지하기 위해 key 개수 먼저 봐준다
        if len(key) != 0 and current_octave == key[s]:

            # key_name 에 있는 값을 넣는다.
            # 조표는 c1, c2 등 옥타브 상관없이
            # 전역 해당 음계(c)까지 적용범위이기 때문
            key_list.append(key_name[s])
            key_num_list.append(key[s])

            s += 1
            next_i = next_accidental(result, i, shape)

            if next_i == 'none':
                # 다음에 있는 노트와 거리 차이를 알아낸다.
                # 조표라면 다음 노트와의 거리가 50 이상이 넘어야 한다.
                distance_note = abs(result[next_note_i]['coordinate'][0]
                                    - result[i]['coordinate'][0])
                # 또한 다음 노트와 현재 모아진 key_num_list 와 같은것이 하나도 없어야 한다
                is_same = True
                for k in range(0, len(key_num_list)):
                    if not key_num_list[k] in note_octave_list:
                        is_same = False
                        break
                # 아래 조건을 충족 한다면 key_signature 에 넣는다
                if distance_note >= 50 or is_same == False:
                    key_signature_dic = {
                        'sharp': [],
                        'flat': [],
                        'natural': []
                    }
                    key_signature_dic[shape] = key_list
                    break

                else:
                    next_i = copy.deepcopy(first_i)
                    key = []
                    continue

        # 일반 올림, 내림표로 쓰이는 임시표인지 확인
        # 확인 방법은 미리 만들어둔 노트 옥타브 리스트와 교집합 비교
        else:
            # octave 을 리스트 형태로 만들어 서로 교집합 비교 가능하게 만듬
            # set 는 둘의 교집합 리스트이다
            set = list({x for x in [current_octave]} &
               {x for x in note_octave_list})
            # 개수가 1개라도 있다면 서로 겹치는게 있다는 뜻
            # 임시표로 넣고 조표 탐색을 중지한다.
            if len(set) >= 1:
                accidental_dic[shape].append(deverse_octave_list[current_octave])

                # 이미 조표에 넣어진 것이라면 다시 지운다
                s = 0
                while True:
                    if s >= len(accidental_dic[shape]):
                        break

                    name = accidental_dic[shape][s][0]

                    if name in key_signature_dic[shape]:
                        del accidental_dic[shape][s]

                    else:
                        s += 1
                break

            # 오류로 넣어진 임시표이므로 무시하고 다음 조표 탐색
            else:
                next_i = next_accidental(result, i, shape)

    return key_signature_dic, accidental_dic, i


def next_accidental(result, i, name_symbol):
    """
    현재 i값 위치에서 바로 다음에 있는
    같은 이름의 임시표를 result 리스트에 찿아
    그 인덱스값 (i) 를 반납

    """
    # 그 전 임시표의 위치를 기억한다
    before_w = result[i]['coordinate'][0]

    while True:
        i += 1
        current_w = result[i]['coordinate'][0]

        # 모든 리스트를 다 돈 경우
        if i > len(result):
            i = 'none'
            break

        # 너무 멀리 떨어져 있어 이어질 수 없다고 판단될때,
        # 혹은 노트가 중간에 발견될 경우
        # 다음 이을 임시표를 못 찾은 경우 이므로 none 반납
        # 90 (노트와 노트 사이의 거리 x 2) (나중에 악보 바뀔때 바꿔야 할지도)
        if abs(current_w - before_w) >= 45 or \
            result[i]['shape'] == 'note':
            i = 'none'
            break

        # 가까운 경우 다음이 같은 임시표라면 이어질 가능성이 있다.
        else:
            # 이어질 수 있는 임시표 위치 발견
            if result[i]['shape'] == name_symbol:
                break

            else:
                continue

    return i


def next_note(result, i):
    """
        현재 i값 위치에서 바로 다음에 있는
        노트를 인덱스에서 찿는다.
        그 인덱스값 (i) 를 반납

    """
    while True:
        i += 1

        if i >= len(result):
            i = 'none'
            break

        if result[i]['shape'] == 'note':
            break

        else:
            continue

    return i


def make_octave_list(result, i):

    octave_list = [result[i]['octave']]

    while True:
        i += 1
        # 다음이 존재하는지 확인
        try:
            exist_next = result[i]

        except IndexError:
            break

        else:
            # 멀티인 경우도 합쳐야 하므로
            if result[i]['shape'] == 'note' and \
                result[i]['note_number'] == 0:
                octave_list.append(result[i]['octave'])

            else:
                break

    return octave_list


def make_octave_name_list(result, i):

    octave_list = [result[i]['octave_name']]

    while True:
        i += 1
        # 다음이 존재하는지 확인
        try:
            exist_next = result[i]

        except IndexError:
            break

        else:
            # 멀티인 경우도 합쳐야 하므로
            if result[i]['shape'] == 'note' and \
                result[i]['note_number'] == 0:
                octave_list.append(result[i]['octave_name'])

            else:
                break

    return octave_list


def key_signature(symbol, clef, key_signature_dic):
    """
    어떤 임시표이며 어떤 음자리표인지 받아서
    나중에 비교로 쓰일 조표 리스트를 만들어낸다.

    """
    if clef == 'treble_clef' and symbol == 'sharp':
        key = [77, 72, 79, 74, 69, 76, 71]
        key_name = ['f', 'c', 'g', 'd', 'a', 'e', 'b']

    elif clef == 'bass_clef' and symbol == 'sharp':
        key = [53, 48, 55, 50, 45, 52, 47]
        key_name = ['f', 'c', 'g', 'd', 'a', 'e', 'b']

    elif clef == 'treble_clef' and symbol == 'flat':
        key = [71, 76, 69, 74, 67, 72, 65]
        key_name = ['b', 'e', 'a', 'd', 'g', 'c', 'f']

    elif clef == 'bass_clef' and symbol == 'flat':
        key = [47, 52, 45, 50, 43, 48, 41]
        key_name = ['b', 'e', 'a', 'd', 'g', 'c', 'f']

    elif symbol == 'natural':
        if len(key_signature_dic['sharp']) >= 1:
            if clef == 'treble_clef':
                key = [77, 72, 79, 74, 69, 76, 71]
                key_name = ['f', 'c', 'g', 'd', 'a', 'e', 'b']
            elif clef == 'bass_clef':
                key = [53, 48, 55, 50, 45, 52, 47]
                key_name = ['f', 'c', 'g', 'd', 'a', 'e', 'b']

        elif len(key_signature_dic['flat']) >= 1:
            if clef == 'treble_clef':
                key = [71, 76, 69, 74, 67, 72, 65]
                key_name = ['b', 'e', 'a', 'd', 'g', 'c', 'f']
            elif clef == 'bass_clef':
                key = [47, 52, 45, 50, 43, 48, 41]
                key_name = ['b', 'e', 'a', 'd', 'g', 'c', 'f']

        else:
            key = []
            key_name = []

    return key, key_name


def general_accidental(result, i, shape, accidental_dic, key_signature_dic):

    # 현재 임시표의 옥타브 값
    current_octave = [result[i]['octave']]
    # 먼저 다음 노트 인덱스 값 알아내고
    next_note_i = next_note(result, i)
    # 옥타브 리스트도 얻어낸다
    if next_note_i == 'none':
        return accidental_dic, i

    note_octave_list = make_octave_list(result, next_note_i)

    # octave 을 리스트 형태로 만들어 서로 교집합 비교 가능하게 만듬
    # set 는 둘의 교집합 리스트이다
    set = list({x for x in current_octave} &
               {x for x in note_octave_list})

    # 개수가 1개라도 있다면 서로 겹치는게 있다는 뜻
    # 임시표에 넣는다.
    if len(set) >= 1:
        accidental_dic[shape].append(
            result[i]['octave_name']
        )

    s = 0
    # 이미 조표에 적용이 되있다면 두번 적용되면 안되므로 임시표에서 다시 지운다
    while True:
        if s >= len(accidental_dic[shape]):
            break

        name = accidental_dic[shape][s][0]

        if name in key_signature_dic[shape]:
            del accidental_dic[shape][s]

        else:
            s += 1

    compare_name = result[i]['octave_name']
    # 임시표에 다른 부분에 이미 적용이 되있다면 그 부분을 지우고
    # 현재 들어간 임시표를 적용시킨다
    for s in range(0, 3):
        if s == 0 and not shape == 'sharp':
            c_name = 'sharp'
        elif s == 1 and not shape == 'flat':
            c_name = 'flat'
        elif s == 2 and not shape == 'natural':
            c_name = 'natural'
        else:
            continue

        j = 0

        while True:
            if j >= len(accidental_dic[c_name]):
                break

            elif compare_name in accidental_dic[c_name][j]:
                del accidental_dic[c_name][j]

            else:
                j += 1

    return accidental_dic, i


def accept_all(result, i, note_octave_name_list,
               key_signature_dic, accidental_dic):
    """

    확인 순서

    1. 조표
        (sharp >> flat >> natural 순으로)

    2. 임시표
        (sharp >> flat >> natural 순으로)

    3. 8va/8vb (23.01.12 나중에 추가)

    4. (추후에 추가될 심볼) ..


    sharp : +1

    flat : -1

    natural: 원본
    (octave_name 은 그대로 일테니 리스트 가져와서 octave 재 수정)

    """
    for s in range(0, len(note_octave_name_list)):
        # t == 0 >> 조표 적용
        # t == 1 >> 임시표 적용
        # t == 2 >> 8va/8vb 적용 (23.01.12 나중에 추가)
        for t in range(0, 2):
            # 옥타브 번호 리스트 중 현재 적용할 번호
            key_list = []
            current_name = note_octave_name_list[s]

            # 조표 sharp
            if t == 0:
                key_list = key_signature_dic['sharp']

            # 임시표 sharp
            elif t == 1:
                key_list = accidental_dic['sharp']

            for k in range(0, len(key_list)):
                # 조표에 적용되는 것이 있다면
                # sharp 이므로 +1 후
                # 더 이상 비교할 필요 없으므로 반복 중지
                # 같은 옥타브인 경우도 적용을 시킨다 (jump_up 악보를 보면 이런식으로 표기 되있을 수 있음)
                # 어차피 불협화음이라 맞춰놓긴 해야함
                if (key_list[k] in current_name) is True or \
                    (t == 0 and key_list[k][0] in current_name):
                    result[i]['octave'] += 1
                    break

            # 조표 flat
            if t == 0:
                key_list = key_signature_dic['flat']

            # 임시표 flat
            elif t == 1:
                key_list = accidental_dic['flat']

            for k in range(0, len(key_list)):
                # flat 이므로 -1
                # 같은 옥타브인 경우도 적용을 시킨다
                # ex) key_list = e2 , current_name = e3 라도 적용
                if (key_list[k] in current_name) is True or \
                        (t == 0 and key_list[k][0] in current_name):
                    result[i]['octave'] -= 1
                    break

            # 조표 natural
            if t == 0:
                key_list = key_signature_dic['natural']

            # 임시표 natural
            elif t == 1:
                key_list = accidental_dic['natural']

            for k in range(0, len(key_list)):
                # 제자리표는 원래 옥타브로 되돌림
                # ex) key_list = e2 , current_name = e3 라도 적용
                if (key_list[k] in current_name) is True or \
                        (t == 0 and key_list[k][0] in current_name):
                    result[i]['octave'] = \
                        octave_list[result[i]['octave_name']]
                    break

        i += 1
    # 다음에 i += 1 하므로
    i -= 1

    return result, i





