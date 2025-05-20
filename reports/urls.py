from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.reports_dashboard, name='reports-dashboard'),
    path('reports/monitor/<int:daytime_id>/', views.reports_monitor, name='reports-monitor'),
]
