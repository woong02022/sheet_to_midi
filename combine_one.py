

def combine_detected(s_list, name):
    # w, h 순으로 정렬 한다
    s_list.sort(key=lambda x: (x[0], x[1]))

    # 일단 비교를 해야 하므로 맨 처음 에는 노트를 넣는 것으로 시작
    if len(s_list) == 0:
        return s_list

    new_list = [[s_list[0]]]

    # s_list 의 시작 인덱스 값
    i = 1

    while True:

        if i >= len(s_list):
            break

        is_combine = False
        for s in range(0, len(new_list)):
            # w 차이는 합쳐진 new_list 중 가장 나중에 들어온
            # 좌표를 선택해 w 순으로 정리 했으므로 가장 가까운 것을 찿는다
            w_diff = abs(s_list[i][0] - new_list[s][-1][0])
            h_diff = abs(s_list[i][1] - new_list[s][-1][1])

            if w_diff <= 14 and h_diff <= 10:
                is_combine = True
                new_list[s].append(list(s_list[i]))
                break

        if is_combine is False:
            new_list.append([s_list[i]])

        i += 1

    for n in range(0, len(new_list)):
        new_list = make_one(new_list, n, name)

    return new_list


def make_one(combine_list, n, name):

    """
    합쳐진 것들중 가장 중간 값을 선정해
    1개로 합친다

    """
    all_w = 0
    all_h = 0

    for i in range(0, len(combine_list[n])):
        all_w += combine_list[n][i][0]
        all_h += combine_list[n][i][1]

    one_w = round(all_w / len(combine_list[n]))
    one_h = round(all_h / len(combine_list[n]))

    combine_list[n] = [one_w, one_h, name]

    return combine_list
