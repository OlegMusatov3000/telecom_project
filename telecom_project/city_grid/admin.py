from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import resolve

from .models import CityGrid, Block, Tower, TowerCoverage

admin.site.unregister(Group)
admin.site.register(Tower)


class TowerCoverageInLine(admin.StackedInline):
    model = TowerCoverage
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'block_for_tower':
            object_id = resolve(request.path_info).kwargs.get('object_id')

            kwargs['queryset'] = Block.objects.filter(
                blocked=False, city_grid_id=object_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(CityGrid)
class CityGridAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'rows', 'columns', 'coverage_threshold', 'show_visualization'
    ]
    list_display_links = list_display
    search_fields = ['coverage_threshold']
    save_on_top = True
    readonly_fields = ('towers',)
    CityGrid.show_visualization.short_description = 'Визуализация'

    def get_inlines(self, request, obj=None):
        if obj:
            return [TowerCoverageInLine]
        return []

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not obj:
            fields.remove('towers')
        elif obj:
            fields.remove('auto_place_towers')
        return fields


@admin.register(Block)
class BlockedBlockAdmin(admin.ModelAdmin):
    list_display = [
        'row', 'column', 'blocked', 'towers_blocked', 'covered_with_a_tower'
    ]
    list_display_links = list_display
    list_filter = ('blocked', 'towers_blocked', 'covered_with_a_tower')
    search_fields = ['city_grid']
    save_on_top = True

    def has_add_permission(self, request):
        return False
