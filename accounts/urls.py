from .views import (
    ProfileView, ProfileEditView, CustomLoginView, CustomLogoutView,
    CustomSignupView,
    StaticPasswordResetView,
    StaticPasswordChangeView
)
from django.urls import path

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('logout/', CustomLogoutView.as_view(), name='account_logout'),
    path('register/', CustomSignupView.as_view(), name='account_register'),
    path('password/reset/', StaticPasswordResetView.as_view(), name='password_reset'),
    path('password/change/', StaticPasswordChangeView.as_view(), name='password_change'),
]
