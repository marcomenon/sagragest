from django.urls import path
from .views import *

urlpatterns = [
    path('rapid/', rapid_dashboard, name='rapid-dashboard'),
    path('rapid/change_category/', rapid_change_category, name='rapid-change-category'),
    path('rapid/move_row/', rapid_move_row, name='rapid-move-row'),
    path('rapid/add_row/', rapid_add_row, name='rapid-add-row'),
    path('rapid/delete_row/', rapid_delete_row, name='rapid-delete-row'),
    path('rapid/move_element/', rapid_move_element, name='rapid-move-element'),
    path('rapid/add_element/', rapid_add_element, name='rapid-add-element'),
    path('rapid/delete_element/', rapid_delete_element, name='rapid-delete-element'),
    path('rapid/order/', rapid_order_entry, name='rapid-order'),
]
