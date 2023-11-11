import matplotlib.pyplot as plt
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib

from .models import Block


def visualize_city_grid(request, city_grid_pk):
    try:
        blocks = Block.objects.filter(city_grid=city_grid_pk)
    except (Block.DoesNotExist):
        return HttpResponse("Tower or coverage not found")
    if plt:
        matplotlib.use('Agg')
    fig, ax = plt.subplots(dpi=300)

    for block in blocks:
        if block.blocked:
            color = 'red'
        elif block.towers_blocked:
            color = 'yellow'
        elif block.covered_with_a_tower:
            color = 'blue'
        else:
            color = 'green'
        ax.add_patch(Rectangle((block.column, block.row), 1, 1, color=color))

    ax.set_xlim(0, max([block.column for block in blocks]) + 1)
    ax.set_ylim(0, max([block.row for block in blocks]) + 1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Столбец в сетке')
    ax.set_ylabel('Строка в сетке')

    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label='Застроенный блок'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='green', markersize=10, label='Свободный блок'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='yellow', markersize=10, label='Расположение вышки'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', markersize=10, label='Покрытая зона вышкой'),
    ]

    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.344, 0.6), bbox_transform=plt.gcf().transFigure)

    plt.subplots_adjust(left=0.4, right=1)
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response
