# # views.py
# from django.shortcuts import render
# from django_plotly_dash import DjangoDash
# from dash import dcc, html
# import plotly.express as px
# import pandas as pd

# from .models import CityGrid, Block, TowerCoverage

# # def visualize_tower_coverage(request, city_grid_id):
# #     # Получите экземпляр CityGrid
# #     city_grid = CityGrid.objects.get(id=city_grid_id)

# #     # Создайте Dash-приложение
# #     app = DjangoDash('VisualizeTowerCoverage')

# #     # Постройте заблокированные и незаблокированные блоки
# #     blocks = Block.objects.filter(city_grid=city_grid)
# #     blocks_data = pd.DataFrame({'row': [block.row for block in blocks],
# #                                 'column': [block.column for block in blocks],
# #                                 'blocked': [block.blocked for block in blocks]})

# #     # Проверка на наличие данных
# #     if not blocks_data.empty:
# #         fig = px.scatter(blocks_data, x='column', y='row', color='blocked',
# #                         labels={'blocked': 'Blocked'},
# #                         title='Tower Coverage Visualization')

# #         # Постройте покрытие вышки
# #         for tower in city_grid.towers.all():
# #             for tower_coverage in TowerCoverage.objects.filter(city_grid=city_grid, tower=tower):
# #                 covered_blocks = tower_coverage.covered_blocks.all()
# #                 covered_blocks_data = pd.DataFrame({'row': [block.row for block in covered_blocks],
# #                                                     'column': [block.column for block in covered_blocks]})

# #                 # Добавление маркеров покрытия вышки
# #                 if not covered_blocks_data.empty:
# #                     fig.add_trace(px.scatter(covered_blocks_data, x='column', y='row',
# #                                             mode='markers', marker=dict(color='blue'), showlegend=False).data[0])
# #     else:
# #         # Логика для случая отсутствия данных
# #         fig = px.scatter()  # или другие действия по вашему усмотрению

# #     # Настройте макет графика
# #     fig.update_layout(
# #         autosize=False,
# #         width=800,
# #         height=600,
# #         margin=dict(l=0, r=0, b=0, t=30),
# #         title_text='Tower Coverage Visualization'
# #     )

# #     # Вставьте график в Dash-приложение
# #     app.layout = html.Div([
# #         dcc.Graph(figure=fig)
# #     ])

# #     return render(request, 'visualize_tower_coverage.html')

import matplotlib.pyplot as plt
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from .models import Block

# class BlockVisualization(View):
#     def get(self, request, *args, **kwargs):
#         # Получаем все объекты Block, например, можно фильтровать по city_grid или другим параметрам
#         blocks = Block.objects.all()

#         # Создаем фигуру и оси
#         fig, ax = plt.subplots()

#         # Перебираем блоки и рисуем квадрат для каждого из них
#         for block in blocks:
#             color = 'red' if block.blocked else 'green'
#             ax.add_patch(plt.Rectangle((block.column, block.row), 1, 1, color=color))

#         # Настраиваем оси и метки
#         ax.set_xlim(0, max([block.column for block in blocks]) + 1)
#         ax.set_ylim(0, max([block.row for block in blocks]) + 1)
#         ax.set_aspect('equal', adjustable='box')
#         ax.set_xlabel('Столбец в сетке')
#         ax.set_ylabel('Строка в сетке')

#         # Создаем объект, который может быть встроен в HttpResponse
#         canvas = FigureCanvasAgg(fig)
#         response = HttpResponse(content_type='image/png')
#         canvas.print_png(response)

#         return response
from django.shortcuts import render
from django.http import HttpResponse
import numpy as np
import matplotlib.pyplot as plt

from .models import Tower, TowerCoverage, Block
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from city_grid.models import Block
import matplotlib.pyplot as plt
import matplotlib

def visualize_tower_coverage(request, tower_pk):
    try:
        blocks = Block.objects.filter(city_grid=tower_pk)
    except (Block.DoesNotExist):
        return HttpResponse("Tower or coverage not found")
    if plt:
        matplotlib.use('Agg')
    fig, ax = plt.subplots()

        # Перебираем блоки и рисуем квадрат для каждого из них
    for block in blocks:
        color = 'red' if block.blocked else 'green'
        ax.add_patch(plt.Rectangle((block.column, block.row), 1, 1, color=color))

    # Настраиваем оси и метки
    ax.set_xlim(0, max([block.column for block in blocks]) + 1)
    ax.set_ylim(0, max([block.row for block in blocks]) + 1)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Столбец в сетке')
    ax.set_ylabel('Строка в сетке')

    # Создаем объект, который может быть встроен в HttpResponse
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response
