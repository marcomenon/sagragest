from django.contrib import admin
from .models import PrinterLayout

@admin.register(PrinterLayout)
class PrinterLayoutAdmin(admin.ModelAdmin):
    list_display = ("name", "printer", "layout_path", "is_user", "event")
    search_fields = ("name",)
    list_filter = ("event", "is_user", "printer", "category")
    readonly_fields = ("layout_path",)
    filter_horizontal = ("category",)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('event').prefetch_related('category')
