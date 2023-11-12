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

    class Meta:
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'
        ordering = ('row', 'column')

    def __str__(self):
        return f'Блок c координатами: {self.row}, {self.column}'


class Tower(models.Model):
    radius = models.PositiveIntegerField(
        'Радиус вышки',
        help_text='Пожалуйста укажите какой радиус охватывает эта вышка'
    )

    class Meta:
        verbose_name = 'Вышка'
        verbose_name_plural = 'Вышки'

    def __str__(self):
        return f'Вышка № {self.id} с радиусом {self.radius}'


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
        blank=True,
    )
    auto_place_towers = models.BooleanField(
        'Автоматическая расстановка вышек', default=False,
        help_text='Установите флажок, если хотите, чтобы вышки расставлялись автоматически.'
    )

    def optimize_tower_placement(self):
        """
        Размещение минимального количества вышек так, чтобы все не загороженные блоки
        находились в пределах действия хотя бы одной вышки.
        """
        free_blocks = Block.objects.filter(
            city_grid=self, blocked=False, towers_blocked=False,
            covered_with_a_tower=False
        )

        while free_blocks.exists():
            target_block = free_blocks.annotate(
                num_uncovered_neighbors=models.Count(
                    'city_grid__blocks',
                    ilter=models.Q(
                        blocked=False, towers_blocked=False,
                        covered_with_a_tower=False
                    )
                )
            ).order_by('-num_uncovered_neighbors').first()

            if target_block is None:
                break

            selected_tower = Tower.objects.annotate(
                ratio=models.F('radius') / models.Value(
                    1, output_field=models.FloatField()
                ),
            ).filter(ratio__isnull=False).order_by('-ratio').first()
            if selected_tower:
                tower_coverage = TowerCoverage.objects.create(
                    tower=selected_tower,
                    city_grid=self,
                    block_for_tower=target_block
                )

                tower_coverage.calculate_coverage()
                free_blocks = Block.objects.filter(
                    city_grid=self, blocked=False, covered_with_a_tower=False
                )

    def show_visualization(self):
        return mark_safe(f'<a href="{reverse("visualize_city_grid", args=[self.pk])}" target="_blank">Показать визуализацию</a>')

    def save(self, *args, **kwargs):
        if not self.pk:
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


# class CityGridTower(models.Model):
#     city_grid = models.ForeignKey(CityGrid, on_delete=models.CASCADE)
#     tower = models.ForeignKey(Tower, on_delete=models.CASCADE)
