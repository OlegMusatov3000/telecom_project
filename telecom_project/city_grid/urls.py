"""
Module: urls.py
Description: Defines path
for the visualization of city grids in the Django web application.

Dependencies:
- path from django.urls
- visualize_city_grid function from .views

"""
from django.urls import path
from .views import visualize_city_grid

urlpatterns = [
    path(
        'visualize_city_grid/<int:city_grid_pk>/',
        visualize_city_grid, name='visualize_city_grid'
    ),
]
