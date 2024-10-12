import mido


def create_midi_file(right_finger, left_finger, tempo=300000):
    """
    bpm 적용을 bar 에서 다음 bar 까지 bpm start 혹은 tempo 를 찾아서
    있으면 그때 적용을 하던지 아니면 그전에 미리 위치를 완벽 하게 세팅 하던지 해야할듯
    """
    mid = mido.MidiFile(type=1)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track_2 = mido.MidiTrack()
    mid.tracks.append(track_2)

    track.append(mido.MetaMessage(type='set_tempo', tempo=tempo, time=0))

    # r_l second
    r_s = 0
    l_s = 0

    remain_r = 0
    remain_l = 0

    total_r = 0
    total_l = 0

    right_i = 0
    left_i = 0

    stop_r = False
    stop_l = False

    right_i, _ = find_next_note_or_rest(right_finger, right_i)
    left_i, _ = find_next_note_or_rest(left_finger, left_i)

    while True:
        if right_i == 'end':
            right_num = 0
            right_w = 0
        else:
            right_num = right_finger[right_i]['note_number']
            right_w = right_finger[right_i]['coordinate'][0]

        if left_i == 'end':
            left_num = 0
            left_w = 0
        else:
            left_num = left_finger[left_i]['note_number']
            left_w = left_finger[left_i]['coordinate'][0]

        same_play = is_same_play(right_finger, left_finger, right_i, left_i)

        # 둘다 끝난 경우 (bar 에 도달)
        if right_i == 'end' and \
                left_i == 'end':
            break

        elif stop_r is True and stop_l is True:
            stop_r = False
            stop_l = False

        # 악보상 서로 같이 처야 되는 표시로 된 경우
        elif same_play is True and not \
            (right_i == 'end' or left_i == 'end') and not \
                (stop_r is True or stop_l is True):

            if right_finger[right_i]['shape'] == 'note':
                r_time = int(mido.second2tick(r_s, 480, tempo))
                track.append(mido.Message
                             ('note_on', note=right_finger[right_i]['octave'],
                              velocity=64, time=r_time))

                r_s = 0

            while True:
                right_i, stop_r = find_next_note_or_rest(right_finger, right_i, stop_r)

                if right_i == 'end':
                    break

                elif right_finger[right_i]['shape'] == 'note' and \
                        right_finger[right_i]['note_number'] == 0:
                    track.append(mido.Message
                                 ('note_on', note=right_finger[right_i]['octave'],
                                  velocity=64, time=0))
                else:
                    break

            if left_finger[left_i]['shape'] == 'note':
                l_time = int(mido.second2tick(l_s, 480, tempo))
                track_2.append(mido.Message
                               ('note_on', note=left_finger[left_i]['octave'],
                                velocity=64, time=l_time))

                l_s = 0
            while True:
                left_i, stop_l = find_next_note_or_rest(left_finger, left_i, stop_l)

                if left_i == 'end':
                    break

                elif left_finger[left_i]['shape'] == 'note' and \
                        left_finger[left_i]['note_number'] == 0:
                    track_2.append(mido.Message
                                   ('note_on', note=left_finger[left_i]['octave'],
                                    velocity=64, time=0))
                else:
                    break

            # 다음 노트 / 쉼표에 쓸 second 를 만든다
            # right 가 클때
            if right_num > left_num:
                remain_r = right_num - left_num
                remain_l = 0

                accept_num = left_num

            # left 가 클때
            elif right_num < left_num:
                remain_l = left_num - right_num
                remain_r = 0

                accept_num = right_num
            # 둘이 같을때
            else:
                accept_num = right_num

            r_s += (tempo / 1000000) * accept_num
            l_s += (tempo / 1000000) * accept_num
            total_r += (tempo / 1000000) * accept_num
            total_l += (tempo / 1000000) * accept_num

        # 서로 따로 치는 경우
        else:

            # 오른쪽 먼저 쳐야 되는 상황 일때
            if not right_i == 'end' and \
                    ((right_w < left_w and stop_r is False) or
                        stop_l is True or left_i == 'end'):
                # remain_r 이 남아있다면 이것까지 second 에 더한다
                # 둘다 같이 진행되어야 하므로 r_s, l_s 둘다 올려준다
                if remain_r > 0:
                    r_s += (tempo / 1000000) * remain_r
                    l_s += (tempo / 1000000) * remain_r
                    remain_r = 0

                r_time = int(mido.second2tick(r_s, 480, tempo))

                if right_finger[right_i]['shape'] == 'note':
                    # right 추가
                    track.append(mido.Message
                                 ('note_on', note=right_finger[right_i]['octave'],
                                  velocity=64, time=r_time))
                    r_s = 0

                while True:
                    right_i, stop_r = find_next_note_or_rest(right_finger, right_i, stop_r)

                    if right_i == 'end':
                        break

                    if right_finger[right_i]['shape'] == 'note' and \
                            right_finger[right_i]['note_number'] == 0:
                        track.append(mido.Message
                                     ('note_on', note=right_finger[right_i]['octave'],
                                      velocity=64, time=0))
                    else:
                        break

                # remain_l 값이 존재 한다면
                if remain_l > 0:
                    # left_remain 뺀값이 남는다면
                    # right remain 을 생성한다
                    if remain_l < right_num:
                        accept_num = remain_l
                        remain_r = right_num - remain_l
                        remain_l = 0
                    else:
                        accept_num = right_num
                        remain_l -= accept_num

                        if remain_l < 0:
                            remain_l = 0

                # 이 경우 인식이 안된 경우 일 수 있음
                else:
                    accept_num = right_num

                # 다음 노트에 쓰일 r_second 값
                r_s += (tempo / 1000000) * accept_num
                # 왼쪽 sec 는 현재 값에서 더한다.
                l_s += (tempo / 1000000) * accept_num

            # 왼쪽 먼저 쳐야 되는 상황 일때
            elif not left_i == 'end' and \
                    ((right_w > left_w and stop_l is False) or
                        stop_r is True or right_i == 'end'):

                if remain_l > 0:
                    r_s += (tempo / 1000000) * remain_l
                    l_s += (tempo / 1000000) * remain_l
                    remain_l = 0

                l_time = int(mido.second2tick(l_s, 480, tempo))

                if left_finger[left_i]['shape'] == 'note':
                    # left 추가
                    track_2.append(mido.Message
                                   ('note_on', note=left_finger[left_i]['octave'],
                                    velocity=64, time=l_time))
                    l_s = 0
                # 복수 노트 일 경우 다음 노트까지 다 처리 해야함
                # 이때 다음 노트로 넘어가므로 넘어가는 절차는 따로 더 안만듬
                while True:
                    left_i, stop_l = find_next_note_or_rest(left_finger, left_i, stop_l)

                    if left_i == 'end':
                        break

                    if left_finger[left_i]['shape'] == 'note' and \
                            left_finger[left_i]['note_number'] == 0:
                        track_2.append(mido.Message
                                       ('note_on', note=left_finger[left_i]['octave'],
                                        velocity=64, time=0))
                    else:
                        break

                # remain_r 값이 존재 한다면
                if remain_r > 0:
                    if remain_r < left_num:
                        accept_num = remain_r
                        remain_l = left_num - remain_r
                        remain_r = 0
                    else:
                        accept_num = left_num
                        remain_r -= accept_num

                        if remain_r < 0:
                            remain_r = 0

                # 이 경우 인식이 안된 경우 일 수 있음
                else:
                    accept_num = left_num

                # 다음 노트에 쓰일 r_second 값
                r_s += (tempo / 1000000) * accept_num
                # 왼쪽 sec 는 현재 값에서 더한다.
                l_s += (tempo / 1000000) * accept_num

    mid.save('new_song.mid')

    return mid


def find_next_note_or_rest(finger, i, stop=False):

    if stop is True:
        return i, stop

    current_w = finger[i]['coordinate'][0]
    i += 1

    while True:
        if i >= len(finger):
            i = 'end'
            break

        if finger[i]['shape'].find('note') >= 0 or \
                finger[i]['shape'].find('rest') >= 0:
            if current_w > finger[i]['coordinate'][0] and \
                    current_w - finger[i]['coordinate'][0] > 100:
                stop = True
            break

        else:
            i += 1

    return i, stop


def is_same_play(right_finger, left_finger, right_i, left_i):

    same_play = False

    if right_i == 'end' or left_i == 'end':
        return same_play

    else:
        right = [right_finger[right_i]['coordinate'][0]]
        left = [left_finger[left_i]['coordinate'][0]]

        while True:
            right_i, _ = find_next_note_or_rest(right_finger, right_i)

            if right_i == 'end':
                break

            elif right_finger[right_i]['shape'] == 'note' and \
                    right_finger[right_i]['note_number'] == 0:
                right.append(right_finger[right_i]['coordinate'][0])

            else:
                break

        right_w = find_approximate_average(right)

        while True:
            left_i, _ = find_next_note_or_rest(left_finger, left_i)

            if left_i == 'end':
                break

            elif left_finger[left_i]['shape'] == 'note' and \
                    left_finger[left_i]['note_number'] == 0:
                left.append(left_finger[left_i]['coordinate'][0])
            else:
                break

        left_w = find_approximate_average(left)

        difference = abs(right_w - left_w)

        if difference <= 20:
            same_play = True

    return same_play


def find_approximate_average(lst):
    lst = sorted(lst)
    approximates = []
    i = 0
    while i < len(lst):
        j = i + 1
        while j < len(lst) and lst[j] - lst[j-1] <= 6:
            j += 1
        if j - i > 1:
            approximates.append(lst[i:j])
        i = j
    approximates_count = [len(x) for x in approximates]
    try:
        max_count = max(approximates_count)
    except ValueError:
        # 만약 approximates_count가 비어있다면 리스트의 평균을 반환합니다.
        return round(sum(lst) / len(lst))
    max_count_indices = [i for i, count in enumerate(approximates_count) if count == max_count]
    max_approximates = [approximates[i] for i in max_count_indices]
    if len(max_approximates) == 1:
        return round(max_approximates[0][0])
    avg_max = round(sum(max_approximates[0]) / len(max_approximates[0]))

    return avg_max


def create_midi_file_2(right_finger, left_finger, tempo=300000):
    mid = mido.MidiFile(type=1)
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track_2 = mido.MidiTrack()
    mid.tracks.append(track_2)

    time_plus = 0
    for i in range(0, len(right_finger)):
        # bpm_start 가 나왔다면 track에 tempo 값을 넣는다
        if right_finger[i]['shape'].find('bpm_start') >= 0 or i == 0:
            # bpm start 표시 가 4분음표 라면 별 다른 계산 없이 바로 옮긴다
            # 2023.02.16 8분음표 등 추가 해야함
            if not right_finger[i]['shape'].find('clef') >= 0 \
                    and right_finger[i]['shape'][-1] == '4':
                tempo = mido.bpm2tempo(right_finger[i]['octave'])

            track.append(mido.MetaMessage(type='set_tempo', tempo=tempo, time=0))

        elif right_finger[i]['shape'] == 'note':

            vel = 64
            note = right_finger[i]['octave']
            if right_finger[i]['note_number'] == 0:
                track.append(mido.Message('note_on', note=note, velocity=vel, time=0))

            else:
                second = (tempo / 1000000) * right_finger[i]['note_number']
                # 현재 time 값은 그 전 time_plus 까지 이므로
                time = time_plus
                # 현재 초 값을 다음 노트에 적용 시키기 위해 time_plus 로 저장해둔다
                time_plus = int(mido.second2tick(second, 480, tempo))
                track.append(mido.Message('note_on', note=note, velocity=vel, time=time))

        # 새 노트 추가 시 나중에 추가될 time_plus 값을 만든다
        elif right_finger[i]['shape'] == 'rest':
            second = (tempo / 1000000) * right_finger[i]['note_number']
            # float >> int 로 바꾼후 계산 (소수점은 버림 으로 처리됨)
            time_plus += int(mido.second2tick(second, 480, tempo))

    time_plus = 0

    for i in range(0, len(left_finger)):
        # bpm_start 가 나왔다면 track에 tempo 값을 넣는다
        if left_finger[i]['shape'].find('bpm_start') >= 0:
            # bpm start 표시 가 4분음표 라면 별 다른 계산 없이 바로 옮긴다
            # 2023.02.16 8분음표 등 추가 해야함
            if left_finger[i]['shape'][-1] == '4':
                tempo = mido.bpm2tempo(left_finger[i]['octave'])

            track_2.append(mido.MetaMessage(type='set_tempo', tempo=tempo, time=0))

        elif left_finger[i]['shape'] == 'note':

            vel = 64
            note = left_finger[i]['octave']
            if left_finger[i]['note_number'] == 0:
                track_2.append(mido.Message('note_on', note=note, velocity=vel, time=0))

            else:
                second = (tempo / 1000000) * left_finger[i]['note_number']
                # 현재 time 값은 그 전 time_plus 까지 이므로
                time = time_plus
                # 현재 초 값을 다음 노트에 적용 시키기 위해 time_plus 로 저장해둔다
                time_plus = int(mido.second2tick(second, 480, tempo))
                track_2.append(mido.Message('note_on', note=note, velocity=vel, time=time))

        # 새 노트 추가 시 나중에 추가될 time_plus 값을 만든다
        elif left_finger[i]['shape'] == 'rest':
            second = (tempo / 1000000) * left_finger[i]['note_number']
            # float >> int 로 바꾼후 계산 (소수점은 버림 으로 처리됨)
            time_plus += int(mido.second2tick(second, 480, tempo))

    mid.save('new_song_3.mid')

    return mid