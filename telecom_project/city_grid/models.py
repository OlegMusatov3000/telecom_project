"""
This module defines the models used in the application.

Models:
- Block: Represents a block in the city grid.
- Tower: Represents a communication tower with a specified radius.
- TowerConnection: Represents a connection between two communication towers.
- CityGrid: Represents the city grid containing blocks and towers.
- TowerCoverage: Represents the coverage of a tower on the city grid.
- BlockTowerCoverage: Represents the coverage of a block by a tower.
"""

import random

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse

from .utils import insert_and_return_coordinates


class Block(models.Model):
    city_grid = models.ForeignKey(
        'CityGrid', on_delete=models.CASCADE, related_name='blocks'
    )
    row = models.PositiveIntegerField('строка в сетке')
    column = models.PositiveIntegerField('столбец в сетке')
    blocked = models.BooleanField(
        'Заблокированный блок?', default=False
    )
    towers_blocked = models.BooleanField(
        'Занят вышкой?', default=False
    )
    covered_with_a_tower = models.BooleanField(
        'покрыт вышкой?', default=False
    )
    start_communication_unit = models.BooleanField(
        'начальная точка связи?', default=False
    )
    end_communication_unit = models.BooleanField(
        'конечная точка связи?', default=False
    )

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'
        ordering = ('row', 'column')

    def __str__(self):
        return f'Блок c координатами: {self.row}, {self.column}'


class Tower(models.Model):
    RADIUS_CHOICES = (
        (1, 'Радиус 1'),
        (2, 'Радиус 2'),
        (3, 'Радиус 3'),
    )

    radius = models.PositiveIntegerField(
        'Радиус вышки',
        choices=RADIUS_CHOICES,
        help_text='Пожалуйста, выберите радиус охвата для этой вышки'
    )

    block_for_tower = models.ForeignKey(
        Block, verbose_name='блок для установки вышки',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Вышка'
        verbose_name_plural = 'Вышки'

    def __str__(self):
        return f'Вышка № {self.id} {self.get_radius_display()}'


class TowerConnection(models.Model):
    source_tower = models.ForeignKey(
        'Tower', on_delete=models.CASCADE, related_name='source_connections',
        verbose_name='Исходная вышка'
    )
    target_tower = models.ForeignKey(
        'Tower', on_delete=models.CASCADE, related_name='target_connections',
        verbose_name='Целевая вышка'
    )
    city_grid = models.ForeignKey('CityGrid', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Связь между вышками'
        verbose_name_plural = 'Связи между вышками'

    def __str__(self):
        return f'Связь между вышками {self.source_tower} и {self.target_tower}'

    def save(self, *args, **kwargs):
        super(TowerConnection, self).save(*args, **kwargs)
        self.source_tower.block_for_tower.start_communication_unit = True
        self.target_tower.block_for_tower.end_communication_unit = True
        self.source_tower.block_for_tower.save(
            update_fields=['start_communication_unit']
        )
        self.target_tower.block_for_tower.save(
            update_fields=['end_communication_unit']
        )


class CityGrid(models.Model):
    rows = models.IntegerField(
        'кол-во строк в сетке',
        validators=[MinValueValidator(1, 'Значение не может быть меньше 1')]
    )
    columns = models.IntegerField(
        'кол-во столбцов в сетке',
        validators=[MinValueValidator(1, 'Значение не может быть меньше 1')]
    )
    coverage_threshold = models.PositiveIntegerField(
        'Максимальный % покрытия', default=30,
        help_text='''
        Пожалуйста укажите максимальный процент загороженности вашей сетки
        '''
    )
    towers = models.ManyToManyField(
        Tower, verbose_name='Вышки которые были размещены на этой сетке',
        blank=True, related_name='citygrid'
    )
    auto_place_towers = models.BooleanField(
        'Автоматическая расстановка вышек', default=False,
        help_text='''
            Установите флажок, если хотите,
            чтобы вышки расставлялись автоматически.
        '''
    )

    def optimize_tower_placement(self):
        # Получаем все свободные блоки в городской сетке
        free_blocks = Block.objects.filter(
            city_grid=self, blocked=False, towers_blocked=False,
            covered_with_a_tower=False
        )

        # Пока есть свободные блоки, размещаем вышку
        while free_blocks.exists():
            # Выбираем свободный блок с максимальным количеством
            # непокрытых соседей
            target_block = free_blocks.annotate(
                num_uncovered_neighbors=models.Count(
                    'city_grid__blocks',
                    filter=models.Q(
                        blocked=False, towers_blocked=False,
                        covered_with_a_tower=False
                    )
                )
            ).order_by('-num_uncovered_neighbors').first()

            if target_block is None:
                break  # Если не осталось свободных блоков, выходим из цикла

            # Проверяем, находится ли блок в краевой части сетки
            is_edge_block = target_block.row in {
                1, self.rows
            } or target_block.column in {1, self.columns}

            # Если блок находится на краю, создаем новую вышку
            # с наименьшим радиусом
            if is_edge_block:
                selected_tower = Tower.objects.create(
                    radius=1, block_for_tower=target_block
                )
            else:
                # Выбираем вышку с максимальным отношением радиуса
                # к количеству свободных соседей
                selected_tower_radius = max(
                    1, min(target_block.num_uncovered_neighbors, 3)
                )  # Выбираем минимум между количеством свободных соседей
                # и максимальным радиусом
                selected_tower = Tower.objects.create(
                    radius=selected_tower_radius, block_for_tower=target_block
                )

            TowerCoverage.objects.create(
                tower=selected_tower,
                city_grid=self,
                block_for_tower=target_block
            )

            free_blocks = Block.objects.filter(
                city_grid=self, blocked=False, covered_with_a_tower=False
            )

    def show_visualization(self):
        return mark_safe(f'''
        <a href="{reverse("visualize_city_grid", args=[self.pk])}" target=
        "_blank">Показать визуализацию</a>
        ''')

    def save(self, *args, **kwargs):
        if not self.pk:
            super(CityGrid, self).save(*args, **kwargs)
            for row in range(1, self.rows + 1):
                for column in range(1, self.columns + 1):
                    if random.randint(1, 100) < self.coverage_threshold:
                        Block.objects.create(
                            city_grid=self, row=row,
                            column=column, blocked=True
                        )
                    else:
                        Block.objects.create(
                            city_grid=self, row=row, column=column
                        )
            if self.auto_place_towers:
                return self.optimize_tower_placement()
        else:
            return super(CityGrid, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Городская сетка'
        verbose_name_plural = 'Городские сетки'

    def __str__(self):
        return f'Городкая сетка №{self.id}'


class TowerCoverage(models.Model):
    tower = models.ForeignKey(
        Tower, verbose_name='Выберите вышку', on_delete=models.CASCADE
    )
    city_grid = models.ForeignKey(CityGrid, on_delete=models.CASCADE)
    covered_blocks = models.ManyToManyField(
        Block, through='BlockTowerCoverage', blank=True
    )
    block_for_tower = models.ForeignKey(
        Block, verbose_name='Выберите блок для установки вышки',
        on_delete=models.CASCADE,
        related_name='block_for_tower',
        help_text='''
        Пожалуйста выберите блок для установки вышки из списка свободных блоков
        '''
    )

    def calculate_coverage(self):
        center_coordinates = (
            self.block_for_tower.column, self.block_for_tower.row
        )
        self.city_grid.towers.add(self.tower)
        if self.covered_blocks.count() != 0:
            for block in self.covered_blocks.get_queryset():
                block.covered_with_a_tower = block.towers_blocked = False
                block.save(
                    update_fields=['covered_with_a_tower', 'towers_blocked']
                )
            self.covered_blocks.clear()

        self.block_for_tower.towers_blocked = True
        self.block_for_tower.save(update_fields=['towers_blocked'])

        blocks = insert_and_return_coordinates(
            center_coordinates, self.tower.radius
        )
        for block in blocks:
            self.covered_blocks.add(block)
            block.covered_with_a_tower = True
            block.save(update_fields=['covered_with_a_tower'])

    def save(self, *args, **kwargs):
        super(TowerCoverage, self).save(*args, **kwargs)
        self.calculate_coverage()

    class Meta:
        verbose_name = 'Размещение вышки'
        verbose_name_plural = 'Размещение вышек'

    def __str__(self):
        return f'Вышка № {self.id} с радиусом {self.tower.radius}'


class BlockTowerCoverage(models.Model):
    towercoverage = models.ForeignKey(TowerCoverage, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
