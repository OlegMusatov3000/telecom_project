import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from city_grid.models import Block


def my_figure(id=None):
    blocks = Block.objects.filter(city_grid=id)
    print(id)
    # Создаем фигуру и оси
    fig, ax = plt.subplots()

    # Перебираем блоки и рисуем квадрат для каждого из них
    for block in blocks:
        color = 'red' if block.blocked else 'green'
        ax.add_patch(Rectangle((block.column, block.row), 1, 1, color=color))

    # Настраиваем оси и метки
    ax.set_xlim(0, max([block.column for block in blocks]) + 1)
    ax.set_ylim(0, max([block.row for block in blocks]) + 1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Столбец в сетке')
    ax.set_ylabel('Строка в сетке')

    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label='Застроенный блок'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='green', markersize=10, label='Свободный блок'),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='blue', markersize=10, label='Расположение вышки'),
    ]

    # Добавляем легенду с bbox_to_anchor
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.0, 0.0))

    return fig
