import random
from math import sqrt

from django_matplotlib import MatplotlibFigureField
from django.db import models
# try:
import matplotlib.pyplot as plt
import matplotlib
# except ImportError:
#     plt = None


class Visualization(models.Model):
    city_grid = models.ForeignKey(
        'CityGrid', verbose_name='Визуализировано для:',
        on_delete=models.CASCADE
    )
    figure = MatplotlibFigureField(figure='my_figure',)

    class Meta:
        verbose_name = verbose_name_plural = 'Визуализация'

    def __str__(self):
        return f'Визуализация для объекта: {self.city_grid}, {self.figure}'


class Block(models.Model):
    city_grid = models.ForeignKey('CityGrid', on_delete=models.CASCADE)
    row = models.PositiveIntegerField('строка в сетке')
    column = models.PositiveIntegerField('столбец в сетке')
    blocked = models.BooleanField(
        'Заблокированный блок?', default=False
    )
    # towers_blocked = models.BooleanField(
    #     'Занят вышкой?', default=False
    # )

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'

    def __str__(self):
        return f'Блок c координатами: {self.row}, {self.column}'


class CityGrid(models.Model):
    rows = models.PositiveIntegerField('Количество строк в сетке')
    columns = models.PositiveIntegerField('Количество столбцов в сетке')
    coverage_threshold = models.PositiveIntegerField(
        'Максимальный % покрытия', default=30
    )
    towers = models.ManyToManyField(
        'Tower', related_name='city_grids', blank=True)
    visualize = models.BooleanField(
        'Визуализировать объект?', default=False
    )

    def my_figure(self):
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle
        from city_grid.models import Block
        blocks = Block.objects.filter(city_grid=self)

        if plt:
            matplotlib.use('Agg')
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

    def save(self, *args, **kwargs):
        super(CityGrid, self).save(*args, **kwargs)

        for row in range(1, self.rows + 1):
            for column in range(1, self.columns + 1):
                if random.randint(1, 100) < self.coverage_threshold:
                    Block.objects.create(
                        city_grid=self, row=row, column=column, blocked=True
                    )
                else:
                    Block.objects.create(
                        city_grid=self, row=row, column=column
                    )
        self.my_figure()
        # if self.visualize:
        #     Visualization.objects.create(
        #         city_grid=self,
        #         figure=MatplotlibFigureField(
        #             figure='my_figure',
        #             plt_args=(self),
        #             fig_width=800,
        #             fig_height=600,
        #             output_type='file'
        #         )
        #     )

    class Meta:
        verbose_name = 'Городская сетка'
        verbose_name_plural = 'Городские сетки'

    def __str__(self):
        return f'Городкая сетка №{self.id}'


class Tower(models.Model):
    radius = models.PositiveIntegerField()


class TowerCoverage(models.Model):
    tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
    city_grid = models.ForeignKey(CityGrid, on_delete=models.CASCADE)
    covered_blocks = models.ManyToManyField(Block, through='BlockTowerCoverage', blank=True)
    center_row = models.PositiveIntegerField()
    center_column = models.PositiveIntegerField()

    def calculate_coverage(self):
        tower = self.tower
        radius = tower.radius
        center_row = self.center_row
        center_column = self.center_column
        covered_blocks = []

        for block in Block.objects.filter(city_grid=self.city_grid):
            row_distance = abs(center_row - block.row)
            col_distance = abs(center_column - block.column)

            distance = sqrt(row_distance ** 2 + col_distance ** 2)

            if distance <= radius:
                block.towers_blocked = True

        for block in covered_blocks:
            self.covered_blocks.add(block)

    def save(self, *args, **kwargs):
        super(TowerCoverage, self).save(*args, **kwargs)
        self.calculate_coverage()


class BlockTowerCoverage(models.Model):
    towercoverage = models.ForeignKey(TowerCoverage, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)



