from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Eventi
    path('events/', views.event_detail, name='event-detail'),
    path('events/form/', views.event_form, name='event-form'),
    path('events/table/', views.event_table, name='event-table'),
    path('events/create/', views.event_create, name='event-create'),
    path('events/edit/<int:pk>/', views.event_edit, name='event-edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event-delete'),
    path('events/import/form/', views.event_import_form, name='event-import-form'),
    path('events/import/', views.event_import, name='event-import'),

    # Import/Export XLSX Eventi
    path('events/export/xlsx/form/', views.event_export_xlsx_form, name='event-export-xlsx-form'),
    path('events/export/xlsx/', views.event_export_xlsx, name='event-export-xlsx'),
    path('events/import/xlsx/form/', views.event_import_xlsx_form, name='event-import-xlsx-form'),
    path('events/import/xlsx/', views.event_import_xlsx, name='event-import-xlsx'),

    # Categorie
    path('categories/', views.category_list, name='category-list'),
    path('categories/create/form/', views.category_create_form, name='category-create-form'),
    path('categories/create/', views.category_create, name='category-create'),
    path('categories/from-template/form/', views.category_from_template_form, name='category-from-template-form'),
    path('categories/from-template/create/<int:event_id>/', views.category_from_template_create, name='category-from-template-create'),
    path('categories/<int:pk>/edit/', views.category_edit_form, name='category-edit-form'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),
    path('categories/delete-unused-templates/', views.delete_unused_category_templates, name='delete-unused-category-templates'),

    # Prodotti
    path('products/', views.product_list, name='product-list'),
    path('products/list/<int:category_id>/', views.product_list_for_category, name='product-list-for-category'),
    path('products/create/form/', views.product_create_form, name='product-create-form'),
    path('products/create/', views.product_create, name='product-create'),
    path('products/from-template/form/', views.product_from_template_form, name='product-from-template-form'),
    path('products/from-template/create/<int:category_id>/', views.product_from_template_create, name='product-from-template-create'),
    path('products/<int:pk>/edit/', views.product_edit_form, name='product-edit-form'),
    path('products/<int:pk>/update/', views.product_edit, name='product-edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product-delete'),
    path('products/delete-unused-templates/', views.delete_unused_product_templates, name='delete-unused-product-templates'),
    
    # Giornate
    path("daytime/", views.current_daytime, name="current-daytime"),
    path("daytime/start/", views.start_daytime, name="start-daytime"),
    path("daytime/<int:pk>/close/", views.close_daytime, name="close-daytime"),
    path("daytime/history/", views.daytime_history, name="daytime-history"),
    path("daytime/card/<int:event_id>/", views.daytime_card, name="daytime-card"),
    
    # Ordini
    path("orders/", views.order_dashboard, name="order-dashboard"),
    path("orders/list/", views.order_list, name="order-list"),
    path("orders/<int:pk>/", views.order_detail, name="order-detail"),
    path("orders/detail/placeholder/", views.order_detail_placeholder, name="order-detail-placeholder"),
    path("orders/daytimes/", views.daytime_options, name="daytime-options"),
    path("orders/action/", views.handle_order_action, name="order-action"),
    path("orders/entry/", views.order_entry_view, name="order-entry"),
    path("orders/entry/<int:order_id>/", views.order_entry_view, name="order-edit-entry"),
    path("orders/get-products/", views.get_products_by_category, name="get-products-by-category"),
    path("orders/submit/", views.submit_order, name="submit-order"),
]
