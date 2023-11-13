'''
Django admin configuration for managing CityGrid, Tower, Block,
TowerConnection, and TowerCoverage models.

This module defines the admin classes and inlines for the specified models.

Classes:
- TowerConnectionInLine: Inline admin class for TowerConnection model.
- TowerCoverageInLine: Inline admin class for TowerCoverage model.
- CityGridAdmin: Admin class for CityGrid model.
- BlockedBlockAdmin: Admin class for Block model.

'''
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import resolve

from .models import (
    CityGrid, Block, Tower, TowerCoverage, TowerConnection,
)

admin.site.unregister(Group)
admin.site.register(Tower)


class TowerConnectionInLine(admin.StackedInline):
    '''
    Inline admin class for TowerConnection model.

    Attributes:
    - model: TowerConnection model.
    - extra: Number of extra forms to display.
    '''
    model = TowerConnection
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        '''
        Customize the form field for foreign keys based on the request.

        Args:
        - db_field: The foreign key field.
        - request: The current request.
        - kwargs: Additional keyword arguments.

        Returns:
        - Form field for the foreign key.
        '''
        if db_field.name in ('source_tower', 'target_tower'):
            object_id = resolve(request.path_info).kwargs.get('object_id')

            kwargs['queryset'] = Tower.objects.filter(
                citygrid=object_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TowerCoverageInLine(admin.StackedInline):
    '''
    Inline admin class for TowerCoverage model.

    Attributes:
    - model: TowerCoverage model.
    - extra: Number of extra forms to display.
    '''
    model = TowerCoverage
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        '''
        Filter blocks based on the citygrid for block_for_tower field.
        '''
        if db_field.name == 'block_for_tower':
            object_id = resolve(request.path_info).kwargs.get('object_id')

            kwargs['queryset'] = Block.objects.filter(
                blocked=False, city_grid_id=object_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(CityGrid)
class CityGridAdmin(admin.ModelAdmin):
    '''
    Admin class for managing CityGrid instances.

    - Displays relevant information in the list view.
    - Defines search fields and read-only fields.
    - Configures inlines based on whether an object is being edited or created.
    '''
    list_display = [
        'id', 'rows', 'columns', 'coverage_threshold', 'show_visualization'
    ]
    list_display_links = list_display
    search_fields = ['coverage_threshold']
    save_on_top = True
    readonly_fields = ('towers',)
    CityGrid.show_visualization.short_description = 'Визуализация'

    def get_inlines(self, request, obj=None):
        '''
        Return inlines based on whether an object is being edited or created.
        '''
        if obj:
            return [TowerConnectionInLine, TowerCoverageInLine]
        return []

    def get_fields(self, request, obj=None):
        '''
        Exclude towers field during object creation and auto_place_towers
        during editing.
        '''
        fields = super().get_fields(request, obj)
        if not obj:
            fields.remove('towers')
        elif obj:
            fields.remove('auto_place_towers')
        return fields


@admin.register(Block)
class BlockedBlockAdmin(admin.ModelAdmin):
    '''
    Admin class for managing Block instances.

    - Displays relevant information in the list view.
    - Defines list filters and search fields.
    - Disables the add permission.
    '''
    list_display = [
        'row', 'column', 'blocked', 'towers_blocked', 'covered_with_a_tower'
    ]
    list_display_links = list_display
    list_filter = ('blocked', 'towers_blocked', 'covered_with_a_tower')
    search_fields = ['city_grid']
    save_on_top = True

    def has_add_permission(self, request):
        '''
        Disable the ability to add new Block instances.
        '''
        return False
