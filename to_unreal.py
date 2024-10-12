from rhythm import *
from slur import *
octave = {
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


def compare_list(final_list):
    i = 0

    while True:
        if len(final_list) <= i:
            break

        if final_list[i][0][2].find('triplet') >= 0 or \
                final_list[i][0][2].find('dot') >= 0 or \
                final_list[i][0][2].find('rest') >= 0 or \
                final_list[i][0][2].find('note') >= 0:
            i += 1

        else:
            del final_list[i]

    return final_list


def start(result, image):
    """
    이 함수에서는 조표와 여러 심볼의 정보를 바탕으로
    수정하기 쉽게 보기 편하도록
    아래와 같이 사전(dic) 형태로 저장 한다.
    new_list = [
    {
    coordinate: [x, y]  # 이미지 인식 좌표 값
    note_number: 1 (4분음표), # 언리얼 에서 계산될 숫자 (박자 계산)
    octave : 27 ,
    name : b4
    shape : note (note / rest / triplet / sharp...)
    }
    
    .
    .
    .
    완벽 분리가 끝났다면 이제

    txt 로 보낼 준비를 해야 하는데

    첫번째로 아직 적용 못한

    rest, symbol, 8va/8vb, triplet, 도돌이표

    등이 있는데

    적용순서는 아래와 같다.

    1. 옥타브 (음계)에 영향을 끼치는 것들

    sharp, flat, 조표, 8va/8vb/16va*, ...


    2. 박자에 영향을 끼치는 것들

    rest, triplet, ....


    3. 연주 순서에 영향을 끼치는 것들

    도돌이표...

    ]
    """

    i = -1

    final_list = []

    while True:
        i += 1

        if i >= len(result):
            break

        note_number = 0
        octave_num = 0
        octave_name = 'none'
        name = 'none'

        # 노트 , rest 찿고 리스트안에 넣는다.
        if result[i][0][2].find('note') >= 0:
            name = 'note'

            for s in range(0, len(result[i])):
                if isinstance(result[i][s], list) and \
                        result[i][s][2].find('note') >= 0:
                    if s == 0:
                        note_number = result[i][-1]

                    # 복수 형태라면 note_number 는 0
                    else:
                        note_number = 0
                    # 23.01.12 whole_note 는 7번째 인덱스가 옥타브 이름이 아님
                    octave_name = result[i][s][-1]
                    octave_num = octave[octave_name]

                    # 이미지 좌표 값 = [w, h]
                    coordinate = [result[i][s][0], result[i][s][1]]
                    note_dic = {
                        'coordinate': coordinate,
                        'note_number': note_number,
                        'octave': octave_num,
                        'octave_name': octave_name,
                        'shape': name
                    }

                    final_list.append(note_dic)

                else:
                    continue
            continue

        elif result[i][0][2].find('rest') >= 0:
            is_note = False

            # 만약 쉼표와 노트가 합쳐져 있는 것이라면
            # 쉼표를 지우고 다시 반복을 한다
            for n in range(0, len(result[i]) - 1):
                if result[i][n][2].find('note') >= 0:
                    is_note = True
                    break

            if is_note is True:
                k = 0
                while True:
                    if k >= len(result[i]) - 1:
                        break

                    elif result[i][k][2].find('rest') >= 0:
                        del result[i][k]

                    else:
                        k += 1
                # i += 1 을 할 것이므로 다시 i -= 1 을 해준다
                i -= 1
                continue

            else:
                name = 'rest'
                # tri 로 미리 작성된 note_num 을 가지고 있다면
                note_number = result[i][-1]

        elif result[i][0][2].find('sharp') >= 0 or \
                result[i][0][2].find('flat') >= 0 or \
                result[i][0][2].find('natural') >= 0:
            name = result[i][0][2]
            octave_name = result[i][0][4]

            if octave_name == 'None':
                continue
            try:
                octave_num = octave[octave_name]
            except KeyError:
                octave_num = 0

        elif result[i][0][2].find('bpm_start') >= 0:
            name = result[i][0][2]
            bpm_num = find_near_right_bpm_num(result, i)
            coordinate = [result[i][0][0], result[i][0][1]]
            # bpm 이 들어갈 정확한 위치를 알아낸다.
            s = decide_locate_bpm(final_list, coordinate)

            note_dic = {
                'coordinate': coordinate,
                'note_number': note_number,
                'octave': bpm_num,
                'octave_name': octave_name,
                'shape': name
            }
            # 아까 만든 s(위치값) 에 넣는다
            final_list.insert(s, note_dic)
            continue

        # 그냥 bpm (start 가 아닌) 을 발견한다면 넘어간다.
        elif result[i][0][2].find('bpm') >= 0:
            continue

        else:
            name = result[i][0][2]
            # 이미지 좌표 값 = [w, h]

        coordinate = [result[i][0][0], result[i][0][1]]

        note_dic = {
            'coordinate': coordinate,
            'note_number': note_number,
            'octave': octave_num,
            'octave_name' : octave_name,
            'shape': name
        }

        final_list.append(note_dic)

    return final_list


def find_near_right_bpm_num(result, i):

    """
    bpm start 로부터 어떤 숫자인지 알려준다
    """
    # bpm 이름이 담길 리스트
    # ex) ['bpm_1', 'bpm_5', 'bpm_9']
    bpm_list = []

    compare_w = result[i][0][0]

    # 첫 start 에서 숫자까지 80 이상 떨어져 있지 않은 것으로 간주
    not_over = 80
    while True:
        i += 1

        current_name = result[i][0][2]
        current_diff = abs(result[i][0][0] - compare_w)

        # 끝에 도달한 경우
        if i > len(result) - 1:
            break

        # bpm 숫자가 발견된 경우
        if current_name.find('bpm') >= 0 \
                and not current_name.find('start') >= 0\
                and current_diff <= not_over:
            # 숫자 발견 이후 이므로 숫자와 숫자 사이의 거리는 50
            not_over = 50
            bpm_list.append(current_name)
            # 발견 직후 이므로 compare_w 가 변경된다
            compare_w = result[i][0][0]

        # 계산 범위를 넘은 경우 break
        elif current_diff > not_over:
            break

        # 아직 계산 범위 이내에서 bpm을 못 찿았다면 계속 진행
        else:
            continue

    bpm_num = make_bpm_number(bpm_list)

    return bpm_num


def make_bpm_number(bpm_list):
    bpm_num = 0

    # 리스트 순서를 반전 시켜 아래
    # 일의 자리, 십의 자리, 백의 자리 계산 순서를 지킨다.
    bpm_list.reverse()

    for i in range(0, len(bpm_list)):
        current_num = int(bpm_list[i][-1])
        if i == 0:
            bpm_num += current_num

        elif i == 1:
            bpm_num += current_num * 10

        # 보통 bpm 은 100의 자리 까지 있는 것으로 간주
        elif i == 2:
            bpm_num += current_num * 100

        elif i == 3:
            bpm_num += current_num * 1000

    return bpm_num


def decide_locate_bpm(final_list, coordinate):
    """
    현재의 위치와 그 전 노트와의 위치를 재고
    """
    bpm_w = coordinate[0] - 40

    i = 1

    while True:
        try:
            name = final_list[-i]['shape']
        except IndexError:
            i = len(final_list)
            break

        if name == 'note':
            note_w = final_list[-i]['coordinate'][0]
            w_diff = abs(bpm_w - note_w)

            if w_diff > 20:
                i = len(final_list)
                break
            else:
                i = len(final_list) - i
                break

        else:
            i += 1

    return i


def accept_octave_2():
    """
    key_signature , flat, sharp, 8va/8vb 등
    옥타브에 영향을 끼치는 것들을 모두 노트에 적용 시킨다.
    """
    while True:
        # 조표 생성
        if i >= len(result):
            break

        # 음자리표 발견시
        elif result[i][0][2].find('clef') >= 0:
            i += 1
            if result[i][0][2] == 'flat' or result[i][0][2] == 'sharp':
                key, key_name, i, m = collect_symbol(result, i, combine_symbol, final_list, name_symbol)
                key, key_name = key_signature(result, key, clef, key_name)
                # key 가 되므로 빈 리스트로 돌린다
                combine_symbol = []

            else:
                continue

            # 이제는 octave 를 찿아서 key, symbol_list 참고 후 재바꿈 후
            # new_list 에 위와 같은 딕셔너리 형태로 넣어준다
            # 이제는 노트 하나하나를 개별로 넣어야 되는것을 잊지말자
            # 7.15 할거.txt 랑 조표, 심볼.txt 를 참고하자

            last = 'false'

            if name == 'rest':
                re = 1
            else:
                re = len(result[i]) + m

            for u in range(0, re):
                if u == re:
                    last = 'true'

                if name == 'note':
                    octave_name = result[i][u][7]
                    octave_num = octave[octave_name]
                    octave_num, combine_symbol, name_symbol = accept_key_and_symbol \
                        (octave_name, octave_num, key, key_name, last, combine_symbol, name_symbol)

                elif name == 'rest':
                    octave_num = 0

                if u != 0:
                    note_number = 0

                # 핑거도 추가해야함
                note_dic = {
                    'note_number': note_number,
                    'octave': octave_num,
                    'shape': name
                }
                final_list.append(note_dic)
            # 다 사용한 심볼은 다시 빈 리스트로
            combine_symbol = []

        # 기호 처리 (sharp, flat, triplet ...)
        else:
            # [51, 56, 49], 'flat', 넘겨진 i값
            combine_symbol, name_symbol, i, final_list = collect_symbol(result, i, combine_symbol,
                                                                        final_list, name_symbol)

        i += 1
    return final_list, make_list, result


def key_signature(result, combine_symbol, clef, symbol):
    global key

    if clef == 'treble_clef' and symbol == 'sharp':
        if len(combine_symbol) == 1 and \
                combine_symbol == [57]:
            key = ['f']

        elif len(combine_symbol) == 2 and \
                combine_symbol == [57, 52]:
            key = ['f', 'c']

        elif len(combine_symbol) == 3 and \
                combine_symbol == [57, 52, 59]:
            key = ['f', 'c', 'g']

        elif len(combine_symbol) == 4 and \
                combine_symbol == [57, 52, 59, 54]:
            key = ['f', 'c', 'g', 'd']

        elif len(combine_symbol) == 5 and \
                combine_symbol == [57, 52, 59, 54, 49]:
            key = ['f', 'c', 'g', 'd', 'a']

        elif len(combine_symbol) == 6 and \
                combine_symbol == [57, 52, 59, 54, 49, 56]:
            key = ['f', 'c', 'g', 'd', 'a', 'e']

        elif len(combine_symbol) == 7 and \
                combine_symbol == [57, 52, 59, 54, 49, 56, 51]:
            key = ['f', 'c', 'g', 'd', 'a', 'e', 'b']

    elif clef == 'bass_clef' and symbol == 'sharp':
        if len(combine_symbol) == 1 and \
                combine_symbol == [21]:
            key = ['f']

        elif len(combine_symbol) == 2 and \
                combine_symbol == [21, 16]:
            key = ['f', 'c']

        elif len(combine_symbol) == 3 and \
                combine_symbol == [21, 16, 23]:
            key = ['f', 'c', 'g']

        elif len(combine_symbol) == 4 and \
                combine_symbol == [21, 16, 23, 18]:
            key = ['f', 'c', 'g', 'd']

        elif len(combine_symbol) == 5 and \
                combine_symbol == [21, 16, 23, 18, 13]:
            key = ['f', 'c', 'g', 'd', 'a']

        elif len(combine_symbol) == 6 and \
                combine_symbol == [21, 16, 23, 18, 13, 20]:
            key = ['f', 'c', 'g', 'd', 'a', 'e']

        elif len(combine_symbol) == 7 and \
                combine_symbol == [21, 16, 23, 18, 13, 20, 15]:
            key = ['f', 'c', 'g', 'd', 'a', 'e', 'b']

    elif clef == 'treble_clef' and symbol == 'flat':
        if len(combine_symbol) == 1 and \
                combine_symbol == [51]:
            key = ['b']

        elif len(combine_symbol) == 2 and \
                combine_symbol == [51, 56]:
            key = ['b', 'e']

        elif len(combine_symbol) == 3 and \
                combine_symbol == [51, 56, 49]:
            key = ['b', 'e', 'a']

        elif len(combine_symbol) == 4 and \
                combine_symbol == [51, 56, 49, 54]:
            key = ['b', 'e', 'a', 'd']

        elif len(combine_symbol) == 5 and \
                combine_symbol == [51, 56, 49, 54, 47]:
            key = ['b', 'e', 'a', 'd', 'g']

        elif len(combine_symbol) == 6 and \
                combine_symbol == [51, 56, 49, 54, 47, 52]:
            key = ['b', 'e', 'a', 'd', 'g', 'c']

        elif len(combine_symbol) == 7 and \
                combine_symbol == [51, 56, 49, 54, 47, 52, 45]:
            key = ['b', 'e', 'a', 'd', 'g', 'c', 'f']

    elif clef == 'bass_clef' and symbol == 'flat':
        if len(combine_symbol) == 1 and \
                combine_symbol == [15]:
            key = ['b']

        elif len(combine_symbol) == 2 and \
                combine_symbol == [15, 20]:
            key = ['b', 'e']

        elif len(combine_symbol) == 3 and \
                combine_symbol == [15, 20, 13]:
            key = ['b', 'e', 'a']

        elif len(combine_symbol) == 4 and \
                combine_symbol == [15, 20, 13, 18]:
            key = ['b', 'e', 'a', 'd']

        elif len(combine_symbol) == 5 and \
                combine_symbol == [15, 20, 13, 18, 11]:
            key = ['b', 'e', 'a', 'd', 'g']

        elif len(combine_symbol) == 6 and \
                combine_symbol == [15, 20, 13, 18, 11, 16]:
            key = ['b', 'e', 'a', 'd', 'g', 'c']

        elif len(combine_symbol) == 7 and \
                combine_symbol == [15, 20, 13, 18, 11, 16, 9]:
            key = ['b', 'e', 'a', 'd', 'g', 'c', 'f']

    # 낼 플랫 부분하자 너무 느려서 오늘 못해... 바탕화면에 만드는과정.txt 있으니까 참고하고
    # 샵 >> 샵 후에 key 함수로 오는게 아니라 그냥 먼저 심볼 합치고 심볼 리스트가 이미 있는 상태에서
    # 다시 심볼 함수로 오게 되면 그때 key 함수로 보내버리자 

    return key, symbol


def collect_symbol(result, i, combine_symbol, final_list, name_symbol):
    try:
        test = result[i + 1]

    except IndexError:
        combine_symbol.append(octave.get(result[i][0][4]))
        name_symbol = result[i][0][2]
        return combine_symbol, name_symbol, i, final_list

    else:
        if result[i][0][2] == 'sharp':
            while True:
                if result[i + 1][0][2] == 'sharp' and \
                        abs(result[i][0][0] - result[i + 1][0][0]) <= 60:
                    combine_symbol.append(octave.get(result[i][0][4]))
                    i += 1

                else:
                    combine_symbol.append(octave.get(result[i][0][4]))
                    name_symbol = 'sharp'
                    break

        elif result[i][0][2] == 'flat':
            while True:
                # 플랫이고 다음 플랫과의 거리가 60 이하 여야 조표 인정
                if result[i + 1][0][2] == 'flat' and \
                        abs(result[i][0][0] - result[i + 1][0][0]) <= 60:
                    combine_symbol.append(octave.get(result[i][0][4]))
                    i += 1

                else:
                    combine_symbol.append(octave.get(result[i][0][4]))
                    name_symbol = 'flat'
                    break

        elif result[i][0][2] == 'natural':
            while True:
                if result[i + 1][0][2] == 'natural' and \
                        abs(result[i][0][0] - result[i + 1][0][0]) <= 60:
                    combine_symbol.append(octave.get(result[i][0][4]))
                    i += 1

                else:
                    combine_symbol.append(octave.get(result[i][0][4]))
                    name_symbol = 'natural'
                    break

        # triplet, dot...
        else:
            final_list.append(result[i])

    return combine_symbol, name_symbol, i, final_list


# 보통 이상하게 겹친 rest (쉼표) 나 dot (스타카토) 에 쓰인다.
def find_interval_and_skip(result, i):
    skip = ''

    if result[i + 1][0][0] - result[i][0][0] <= 10:
        i += 1
        skip = 'true'

    return i, skip


def accept_key_and_symbol(octave_name, octave_num, key, key_name, last,
                          list_symbol=None, name_symbol=None):
    # octave = 'e5' , list = ['f', 'c', 'g', 'd', 'a', 'e', 'b']
    # 나중에 더블 샵, 더블 플랫 등등 추가되어야 할 요소 있음

    if name_symbol is None:
        name_symbol = []
    if list_symbol is None:
        list_symbol = []

    octave_0 = octave_name[0]
    natural = octave_num

    # 키 후에 심볼
    # ex) octave_0 = [b] , list_key = ['b', 'e', 'a']
    if octave_0 in key:
        if key_name == 'sharp':
            octave_num += 1

        elif key_name == 'flat':
            octave_num -= 1

    # ex) octave_num = 51, list_symbol = [51, 56, 49]
    if natural in list_symbol:
        if name_symbol == 'sharp':
            octave_num += 1

        elif name_symbol == 'flat':
            octave_num -= 1

        elif name_symbol == 'natural':
            octave_num = natural

        # 다 사용한 심볼값을 원래대로 돌려놓는다.
        if last == 'true':
            list_symbol = []
            name_symbol = None

    return octave_num, list_symbol, name_symbol


def make_note_number(result, i):

    name = result[i][0][2]

    if name.find('whole') >= 0:
        return note['1']

    elif name.find('half') >= 0:
        return note['2']

    elif name.find('quarter') >= 0:
        # rest 인 경우 이름 자체에 ?th 가 써져 있다
        if name.find('rest') >= 0:
            name_2 = name
        # note 인 경우 따로 리스트 맨 끝에 표기해놨다
        else:
            name_2 = result[i][-1]

        if name_2.find('4th') >= 0:
            return note['4']

        elif name_2.find('8th') >= 0:
            return note['8']

        elif name_2.find('16th') >= 0:
            return note['16']

        elif name_2.find('32th') >= 0:
            return note['32']

        elif name_2.find('64th') >= 0:
            return note['64']

        elif name_2.find('128th') >= 0:
            return note['128']


def multi_combine(final_list):
    i = 0

    while True:
        if len(final_list) <= i:
            break

        if isinstance(final_list[i], list):
            i += 1
            continue

        # 마지막 노트라면
        if len(final_list) == i + 1:
            break

        # 리스트 형식이면 dot, triplet 임
        if isinstance(final_list[i + 1], list):
            i_2 = i + 2
            while True:
                if isinstance(final_list[i_2], list):
                    i_2 += 1
                else:
                    break
        else:
            i_2 = i + 1

        if final_list[i_2]['note_number'] == 0 and \
                final_list[i_2]['shape'] == 'note':
            new_octave = [final_list[i]['octave'],
                          final_list[i_2]['octave']]
            del final_list[i_2]
            while True:
                # 다음이 마지막 노트이거나, triplet, dot 라면
                if len(final_list) == i + 1 or \
                        isinstance(final_list[i_2], list) == True:
                    break

                if final_list[i_2]['note_number'] == 0 and \
                        final_list[i_2]['shape'] == 'note':
                    new_octave.append(final_list[i_2]['octave'])
                    del final_list[i_2]

                else:
                    break
            final_list[i]['octave'] = new_octave
            i = i_2

        elif final_list[i_2]['note_number'] == 0 and \
                final_list[i_2]['shape'] == 'rest':
            del final_list[i_2]

        else:
            i = i_2
            continue

    return final_list


def combine_rest(final_list):
    i = 0

    # 처음 나오는 모든 쉼표들은 건너뛴다.
    # 건너뛰는 이유는 만약 처음 쉼표를 모른다면 왼손과 오른손의 시작이 어떻게 되는지 알 수 없다.
    while True:
        if final_list[i]['shape'] == 'rest':
            i += 1

        else:
            break

    while True:
        if len(final_list) <= i + 1:
            if final_list[i]['shape'] == 'rest':
                del final_list[i]

            break

        if final_list[i]['shape'] == 'rest':
            while True:

                if final_list[i]['shape'] == 'rest':
                    if final_list[i]['note_number'] != 0:
                        new_number = final_list[i]['note_number'] + \
                                     final_list[i - 1]['note_number']

                        final_list[i - 1]['note_number'] = new_number
                        del final_list[i]

                    else:
                        del final_list[i]

                else:
                    i += 1
                    break

        else:
            i += 1

    return final_list

