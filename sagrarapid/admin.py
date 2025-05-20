from django.contrib import admin
from .models import RapidInterface, RapidRows, RapidElements

@admin.register(RapidInterface)
class RapidInterfaceAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "category_event")
    search_fields = ("event__name", "category_event__category__name")
    list_filter = ("event", "category_event")

@admin.register(RapidRows)
class RapidRowsAdmin(admin.ModelAdmin):
    list_display = ("id", "rapid_interface", "row_position", "elements_count")
    search_fields = ("rapid_interface__event__name",)
    list_filter = ("rapid_interface",)

    def elements_count(self, obj):
        return obj.elements.count()
    elements_count.short_description = "N. elementi"

@admin.register(RapidElements)
class RapidElementsAdmin(admin.ModelAdmin):
    list_display = ("id", "product_event", "position")
    search_fields = ("product_event__product__name",)
    list_filter = ("product_event__event", "product_event__category")
