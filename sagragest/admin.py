from import_export.admin import ImportExportModelAdmin
from .resources import EventFullResource, CategoryTemplateResource, ProductTemplateResource, CategoryEventResource, ProductEventResource, DaytimeResource, OrderResource, OrderItemResource
from django.contrib import admin
from .models import (
    Event, CategoryTemplate, ProductTemplate,
    CategoryEvent, ProductEvent,
    Daytime, Order, OrderItem
)

@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_class = EventFullResource
    list_display = ("name", "year", "active", "group")
    list_filter = ("active", "year", "group")
    search_fields = ("name",)

@admin.register(CategoryTemplate)
class CategoryTemplateAdmin(ImportExportModelAdmin):
    resource_class = CategoryTemplateResource
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(ProductTemplate)
class ProductTemplateAdmin(ImportExportModelAdmin):
    resource_class = ProductTemplateResource
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(CategoryEvent)
class CategoryEventAdmin(ImportExportModelAdmin):
    resource_class = CategoryEventResource
    list_display = ("category", "event", "display_order")
    list_filter = ("event",)
    search_fields = ("category__name",)

@admin.register(ProductEvent)
class ProductEventAdmin(ImportExportModelAdmin):
    resource_class = ProductEventResource
    list_display = ("product", "event", "category", "price", "display_order")
    list_filter = ("event", "category")
    search_fields = ("product__name",)

@admin.register(Daytime)
class DaytimeAdmin(ImportExportModelAdmin):
    resource_class = DaytimeResource
    list_display = ("event", "start", "end")
    list_filter = ("event",)

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = ("number", "daytime", "status", "total", "is_takeaway")
    list_filter = ("status", "is_takeaway", "daytime")

@admin.register(OrderItem)
class OrderItemAdmin(ImportExportModelAdmin):
    resource_class = OrderItemResource
    list_display = ("order", "product_event", "quantity", "price_at_order_time")