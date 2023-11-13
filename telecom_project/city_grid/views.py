'''
Module: views.py
Description: Contains Django views for visualizing city grids using matplotlib.

Dependencies:
- matplotlib
- numpy
- django.http.HttpResponse
- matplotlib.backends.backend_agg.FigureCanvasAgg
- matplotlib.patches.Rectangle

Models:
- Block
- CityGrid

Utilities:
- find_points_until_end
- get_block_color
- set_axis_limits
- add_legend
'''

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Rectangle

from .models import Block, CityGrid
from .utils import (
    find_points_until_end, get_block_color, set_axis_limits, add_legend
)


def visualize_city_grid(request, city_grid_pk):
    '''
    View function to generate and render a visual representation
    of a city grid.

    Parameters:
    - request: HttpRequest object
    - city_grid_pk: Primary key of the CityGrid instance to visualize

    Returns:
    - HttpResponse with the generated image of the city grid
    '''
    try:
        city_grid = CityGrid.objects.get(id=city_grid_pk)
    except CityGrid.DoesNotExist:
        return HttpResponse('CityGrid not found')

    if plt:
        matplotlib.use('Agg')
    fig, ax = plt.subplots(dpi=300)

    blocks = Block.objects.filter(city_grid=city_grid)

    for block in blocks:
        color = get_block_color(block)
        ax.add_patch(Rectangle((block.column, block.row), 1, 1, color=color))

    set_axis_limits(ax, blocks)

    start_block = Block.objects.filter(
        city_grid=city_grid, start_communication_unit=True
    ).first()
    end_block = Block.objects.filter(
        city_grid=city_grid, end_communication_unit=True
    ).first()

    if start_block and end_block:
        start = (start_block.column, start_block.row)
        end = (end_block.column, end_block.row)

        points = [
            (block.column, block.row) for block in blocks if (
                block.towers_blocked
            )
        ]

        path = find_points_until_end(end, start, points)

        path = np.array(path) + 0.5
        ax.plot(
            path[:, 0], path[:, 1], linestyle='-', color='purple', linewidth=1
        )

    add_legend(ax)

    plt.subplots_adjust(left=0.4, right=1)
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response
