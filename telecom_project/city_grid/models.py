import random
from math import sqrt

from django.db import models


class Block(models.Model):
    city_grid = models.ForeignKey('CityGrid', on_delete=models.CASCADE)
    row = models.PositiveIntegerField('строка в сетке')
    column = models.PositiveIntegerField('столбец в сетке')
    blocked = models.BooleanField(
        'Заблокированный блок?', default=False
    )

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'

    def __str__(self):
        return f'Блок принадлежит {self.city_grid}'


class CityGrid(models.Model):
    rows = models.PositiveIntegerField('Количество строк в сетке')
    columns = models.PositiveIntegerField('Количество столбцов в сетке')
    coverage_threshold = models.PositiveIntegerField(
        'Максимальный % покрытия', default=30
    )
    towers = models.ManyToManyField(
        'Tower', related_name='city_grids', blank=True)

    def place_tower(self, row, column):
        tower = Tower.objects.create(radius=3)  # Пример радиуса вышки
        self.towers.add(tower)

        # Определите область покрытия вышки
        tower_coverage = TowerCoverage.objects.create(
            tower=tower, city_grid=self
        )
        tower_coverage.calculate_coverage(row, column)

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
    covered_blocks = models.ManyToManyField(Block, blank=True)

    def calculate_coverage(self, center_row, center_column):
        tower = self.tower
        radius = tower.radius

        # Очищаем предыдущие блоки в зоне покрытия
        self.covered_blocks.clear()

        # Проходим по всем блокам в сетке
        for block in Block.objects.filter(city_grid=self.city_grid):
            row_distance = abs(center_row - block.row)
            col_distance = abs(center_column - block.column)

            # Рассчитываем расстояние между центром вышки и блоком
            distance = sqrt(row_distance ** 2 + col_distance ** 2)

            # Если расстояние меньше или равно радиусу вышки, то блок находится в зоне покрытия
            if distance <= radius:
                self.covered_blocks.add(block)
