from django.contrib import admin
from django.contrib.auth.models import Group

from .models import CityGrid, Block, Tower, TowerCoverage, BlockTowerCoverage, Visualization

admin.site.unregister(Group)
admin.site.register(Tower)


@admin.register(Visualization)
class VisualizationAdmin(admin.ModelAdmin):
    list_display = ['id']
    list_display_links = list_display
    search_fields = ['id']
    save_on_top = True

    def has_add_permission(self, request):
        return False


class BlockTowerCoverageInLine(admin.StackedInline):
    model = BlockTowerCoverage
    extra = 0


@admin.register(CityGrid)
class CityGridAdmin(admin.ModelAdmin):
    list_display = ['id', 'rows', 'columns', 'coverage_threshold']
    list_display_links = list_display
    search_fields = ['coverage_threshold']
    save_on_top = True


@admin.register(Block)
class BlockedBlockAdmin(admin.ModelAdmin):
    list_display = ['row', 'column', 'blocked']
    list_display_links = list_display
    list_filter = ('blocked',)
    search_fields = ['city_grid']
    save_on_top = True

    def has_add_permission(self, request):
        return False


@admin.register(TowerCoverage)
class TowerCoverageAdmin(admin.ModelAdmin):
    inlines = (BlockTowerCoverageInLine,)
