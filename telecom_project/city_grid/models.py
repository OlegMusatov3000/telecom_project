import random

from django.db import models


class BlockedBlock(models.Model):
    city_grid = models.ForeignKey('CityGrid', on_delete=models.CASCADE)
    row = models.PositiveIntegerField('строка в сетке')
    column = models.PositiveIntegerField('столбец в сетке')

    class Meta:
        verbose_name = 'Заблокированный Блок'
        verbose_name_plural = 'Заблокированные Блоки'

    def __str__(self):
        return f'Заблокированный Блок принадлежит {self.city_grid}'


class CityGrid(models.Model):
    rows = models.PositiveIntegerField('Количество строк в сетке')
    columns = models.PositiveIntegerField('Количество столбцов в сетке')
    coverage_threshold = models.PositiveIntegerField(
        'Минимальный % покрытия', default=30
    )

    def save(self, *args, **kwargs):
        super(CityGrid, self).save(*args, **kwargs)

        for row in range(1, self.rows + 1):
            for column in range(1, self.columns + 1):
                if random.randint(1, 100) < self.coverage_threshold:
                    BlockedBlock.objects.create(
                        city_grid=self, row=row, column=column
                    )

    class Meta:
        verbose_name = 'Городская сетка'
        verbose_name_plural = 'Городские сетки'

    def __str__(self):
        return f'Городкая сетка №{self.id}'
