from django.contrib import admin
from django.urls import path, include
from allauth.account.decorators import secure_admin_login
from django.views.generic import TemplateView

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('', include('printers.urls')),
    path('', include('sagragest.urls')),
    path('', include('sagrarapid.urls')),
    path('', include('reports.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
