from django.conf import settings
from django.contrib.sites.models import Site
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def superadmin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_staff:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def authenticated_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_user_role(user):
    if user.is_superuser:
        return 'superadmin'
    elif user.is_staff:
        return 'admin'
    elif user.is_authenticated:
        return 'user'
    return 'anonymous'

def site_name(request):
    try:
        site = Site.objects.get(id=settings.SITE_ID)
        return {'site_name': site.name}
    except Site.DoesNotExist:
        return {'site_name': 'Django Boilerplate'}

def theme(request):
    theme = "aqua"
    if request.user.is_authenticated:
        theme = request.user.theme or "aqua"
    return {"theme": theme}