from django.urls import path
from . import views

app_name = "printers"

urlpatterns = [
    path("printerslayouts/", views.printlayout_list, name="printlayout_list"),
    path("printerslayouts/create/", views.printlayout_create, name="printlayout_create"),
    path("printerslayouts/<int:pk>/edit/", views.printlayout_update, name="printlayout_update"),
    path("printerslayouts/<int:pk>/delete/", views.printlayout_delete, name="printlayout_delete"),
    path("printerslayouts/form/", views.printlayout_form, name="printlayout_form"),
]
