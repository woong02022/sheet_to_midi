import itertools

# Vars
origin = {'x': 0, 'y': 0}


def slope(origin, target):
    if target['x'] == origin['x']:
        return 0
    else:
        m = (target['y'] - origin['y']) / (target['x'] - origin['x'])
        return m


def line_eqn(origin, target):
    x = origin['x']
    y = origin['y']
    c = -(slope(origin, target) * x - y)
    c = y - (slope(origin, target) * x)
    # return 'y = ' + str(slope(target)) + 'x + ' + str(c)
    m = slope(origin, target)
    return {'m': m, 'c': c}


def get_y(x, slope, c):
    # y = mx + c
    y = (slope * x) + c
    return y


def get_x(y, slope, c):
    # x = (y-c)/m
    if slope == 0:
        c = 0  # vertical lines never intersect with y-axis
    if slope == 0:
        slope = 1  # Do NOT divide by zero
    x = (y - c) / slope
    return x


def get_points(point_1, point_2):
    coord_list = []

    origin = {'x': point_1[0], 'y': point_1[1]}
    target = {'x': point_2[0], 'y': point_2[1]}

    # Step along x-axis
    for i in range(origin['x'], target['x'] + 1):
        eqn = line_eqn(origin, target)
        y = get_y(i, eqn['m'], eqn['c'])
        coord_list.append([i, y])

    # Step along y-axis
    for i in range(origin['y'], target['y'] + 1):
        eqn = line_eqn(origin, target)
        x = get_x(i, eqn['m'], eqn['c'])
        coord_list.append([x, i])

    # return unique list
    return list(k for k, _ in itertools.groupby(sorted(coord_list)))


def get_line_points_list(point_1, point_2):

    points_list = get_points(point_1, point_2)

    rounded_numbers = [[round(num) for num in sublist] for sublist in points_list]

    unique_lists = []
    for sublist in rounded_numbers:
        if sublist not in unique_lists:
            unique_lists.append(sublist)

    return unique_lists
