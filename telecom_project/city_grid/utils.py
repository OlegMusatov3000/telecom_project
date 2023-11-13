'''
Utility functions for visualizing city grids.

Functions:
- find_points_until_end(target_point, end_point, points):
  Finds the nearest points from the target point until reaching the end point.

- insert_and_return_coordinates(center_coordinates, offset):
  Inserts and returns coordinates based on the center coordinates and offset.

- get_block_color(block):
  Determines the color of a block based on its attributes (
    blocked, covered_with_a_tower, etc.
  ).

- set_axis_limits(ax, blocks):
  Sets axis limits for a matplotlib axis based on the provided blocks.

- add_legend(ax):
  Adds a legend to the matplotlib axis with predefined elements for different
  block types.
'''
import heapq
import math

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt


def find_points_until_end(target_point, end_point, points):
    '''
    Finds the nearest points from the target point until reaching
    the end point.

    Args:
        target_point (tuple): The starting point for finding nearest points.
        end_point (tuple): The point at which the search should end.
        points (list): List of points to search through.

    Returns:
        list: List of nearest points from the target point to the end point.
    '''
    if not points:
        return []

    result = []
    points_copy = list(points)

    while target_point != end_point:

        heap = []
        for point in points_copy:
            distance = math.sqrt((target_point[0] - point[0]) ** 2 + (
                target_point[1] - point[1]
            ) ** 2)
            heapq.heappush(heap, (distance, point))

        nearest_point = heapq.heappop(heap)[1]
        result.append(nearest_point)

        target_point = nearest_point

        points_copy.remove(nearest_point)

    return result


def insert_and_return_coordinates(center_coordinates, offset):
    '''
    Inserts and returns coordinates based on the center coordinates and offset.

    Args:
        center_coordinates (tuple): The center coordinates for inserting
        coordinates.
        offset (int): The offset used to calculate the range of coordinates.

    Returns:
        list: List of coordinates generated around the center coordinates.
    '''
    from .models import Block
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

    blocks = Block.objects.filter(
            column__in=[coord[0] for coord in xy],
            row__in=[coord[1] for coord in xy]
        )
    return blocks


def get_block_color(block):
    '''
    Determines the color of a block based on its attributes.

    Args:
        block: An instance of the Block model.

    Returns:
        str: Color code representing the block type.
    '''
    if block.blocked and block.covered_with_a_tower:
        return 'orange'
    elif block.blocked:
        return 'red'
    elif block.towers_blocked:
        return 'yellow'
    elif block.covered_with_a_tower:
        return 'blue'
    else:
        return 'green'


def set_axis_limits(ax, blocks):
    '''
    Sets axis limits for a matplotlib axis based on the provided blocks.

    Args:
        ax: Matplotlib axis.
        blocks (list): List of Block objects.

    Returns:
        None
    '''
    ax.set_xlim(0, max([block.column for block in blocks]) + 1)
    ax.set_ylim(0, max([block.row for block in blocks]) + 1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Столбец в сетке')
    ax.set_ylabel('Строка в сетке')


def add_legend(ax):
    '''
    Adds a legend to the matplotlib axis with predefined elements
    for different block types.

    Args:
        ax: Matplotlib axis.

    Returns:
        None
    '''
    legend_elements = [
        Line2D(
            [0], [0], marker='s', color='w', markerfacecolor='red',
            markersize=10, label='Застроенный блок'
        ),
        Line2D(
            [0], [0], marker='s', color='w', markerfacecolor='green',
            markersize=10, label='Свободный блок'
        ),
        Line2D(
            [0], [0], marker='s', color='w', markerfacecolor='yellow',
            markersize=10, label='Расположение вышки'
        ),
        Line2D(
            [0], [0], marker='s', color='w', markerfacecolor='blue',
            markersize=10, label='Покрытая зона вышкой'
        ),
        Line2D(
            [0], [0], marker='s', color='w', markerfacecolor='orange',
            markersize=10, label='Застроенный блок,\nпокрытый вышкой'
        ),
        Line2D(
            [0], [0], marker='s', color='w', markerfacecolor='purple',
            markersize=10, label='Связь между вышками'
        )
    ]

    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(
        0.344, 0.6
    ), bbox_transform=plt.gcf().transFigure)
