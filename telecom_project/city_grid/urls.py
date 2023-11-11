from django.urls import path
from .views import visualize_tower_coverage

urlpatterns = [
    # path('visualize/<int:city_grid_id>/', visualize_tower_coverage, name='visualize_tower_coverage'),
    # path('block-visualization/', BlockVisualization.as_view(), name='block-visualization'),
    path('visualize_coverage/<int:tower_pk>/', visualize_tower_coverage, name='visualize_tower_coverage'),
]
