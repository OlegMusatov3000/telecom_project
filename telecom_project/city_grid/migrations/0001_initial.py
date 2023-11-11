# Generated by Django 4.2.7 on 2023-11-11 05:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.PositiveIntegerField(verbose_name='строка в сетке')),
                ('column', models.PositiveIntegerField(verbose_name='столбец в сетке')),
                ('blocked', models.BooleanField(default=False, verbose_name='Заблокированный блок?')),
            ],
            options={
                'verbose_name': 'Блок',
                'verbose_name_plural': 'Блоки',
            },
        ),
        migrations.CreateModel(
            name='BlockTowerCoverage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='city_grid.block')),
            ],
        ),
        migrations.CreateModel(
            name='CityGrid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rows', models.PositiveIntegerField(verbose_name='Количество строк в сетке')),
                ('columns', models.PositiveIntegerField(verbose_name='Количество столбцов в сетке')),
                ('coverage_threshold', models.PositiveIntegerField(default=30, verbose_name='Максимальный % покрытия')),
                ('visualize', models.BooleanField(default=False, verbose_name='Визуализировать объект?')),
            ],
            options={
                'verbose_name': 'Городская сетка',
                'verbose_name_plural': 'Городские сетки',
            },
        ),
        migrations.CreateModel(
            name='Tower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('radius', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Visualization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_grid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='city_grid.citygrid', verbose_name='Визуализировано для:')),
            ],
            options={
                'verbose_name': 'Визуализация',
                'verbose_name_plural': 'Визуализация',
            },
        ),
        migrations.CreateModel(
            name='TowerCoverage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('center_row', models.PositiveIntegerField()),
                ('center_column', models.PositiveIntegerField()),
                ('city_grid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='city_grid.citygrid')),
                ('covered_blocks', models.ManyToManyField(blank=True, through='city_grid.BlockTowerCoverage', to='city_grid.block')),
                ('tower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='city_grid.tower')),
            ],
        ),
        migrations.AddField(
            model_name='citygrid',
            name='towers',
            field=models.ManyToManyField(blank=True, related_name='city_grids', to='city_grid.tower'),
        ),
        migrations.AddField(
            model_name='blocktowercoverage',
            name='towercoverage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='city_grid.towercoverage'),
        ),
        migrations.AddField(
            model_name='block',
            name='city_grid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='city_grid.citygrid'),
        ),
    ]
