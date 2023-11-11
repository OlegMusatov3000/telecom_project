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


# def insert_and_return_coordinates(grid_height, grid_width, center_coordinates, offset):
#     center_x, center_y = center_coordinates

#     matrix_size = offset * 2 + 1

#     target_matrix = [[0] * grid_width for _ in range(grid_height)]

#     bottom_left_x = center_x - offset - 1
#     bottom_left_y = center_y - offset - 1

#     xy = []

#     for i in range(1, matrix_size + 1):
#         for j in range(1, matrix_size + 1):
#             target_x = bottom_left_x + i
#             target_y = bottom_left_y + j
#             xy.append((target_y, target_x,))

#             if 0 <= target_x < grid_height and 0 <= target_y < grid_width:
#                 target_matrix[grid_height - 1 - target_x][target_y] = 1  # Можно использовать любое значение

#     return target_matrix, xy

# grid_height, grid_width = 10, 10
# center_coordinates = (10, 1)
# offset = 2

# result_matrix, xy_coordinates = insert_and_return_coordinates(grid_height, grid_width, center_coordinates, offset)

# for row in result_matrix:
#     print(row)

# print(xy_coordinates)
