from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CityGrid, BlockedBlock

admin.site.unregister(Group)


@admin.register(CityGrid)
class CityGridAdmin(admin.ModelAdmin):
    list_display = ['rows', 'columns', 'coverage_threshold']
    list_display_links = list_display
    search_fields = ['coverage_threshold']
    save_on_top = True


@admin.register(BlockedBlock)
class BlockedBlockAdmin(admin.ModelAdmin):
    list_display = ['row', 'column']
    list_display_links = list_display
    search_fields = ['city_grid']
    save_on_top = True

    def has_add_permission(self, request):
        return False
