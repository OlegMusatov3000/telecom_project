# Generated by Django 4.2.7 on 2023-11-09 05:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('city_grid', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blockedblock',
            options={'verbose_name': 'Заблокированный Блок', 'verbose_name_plural': 'Заблокированные Блоки'},
        ),
        migrations.AlterModelOptions(
            name='citygrid',
            options={'verbose_name': 'Городская сетка', 'verbose_name_plural': 'Городскеи сетки'},
        ),
    ]