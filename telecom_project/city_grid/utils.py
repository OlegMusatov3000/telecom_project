def insert_and_return_coordinates(center_coordinates, offset):
    center_x, center_y = center_coordinates

    matrix_size = offset * 2 + 1

    bottom_left_x = center_x - offset - 1
    bottom_left_y = center_y - offset - 1

    xy = []

    for i in range(1, matrix_size + 1):
        for j in range(1, matrix_size + 1):
            target_x = bottom_left_x + i
            target_y = bottom_left_y + j

            xy.append((target_x, target_y))

    return xy
