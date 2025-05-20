from django.urls import reverse_lazy
from allauth.account.views import LoginView, LogoutView, SignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth import get_user_model
from .forms import UserProfileForm, CustomSignupForm, StaticPasswordResetForm, StaticPasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from core.utils import superadmin_required

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('dashboard')

class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'
    next_page = reverse_lazy('account_login')

class CustomSignupView(SignupView):
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('account_login')

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

class StaticPasswordResetView(TemplateView):
    template_name = 'accounts/password_reset.html'

    @method_decorator(superadmin_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = StaticPasswordResetForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = StaticPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                user.set_password('SagraGest1234')
                user.save()
                messages.success(request, f"Password per '{username}' reimpostata con successo.")
            except User.DoesNotExist:
                messages.error(request, f"Utente '{username}' non trovato.")
            return redirect('password_reset')
        return render(request, self.template_name, {'form': form})

class StaticPasswordChangeView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/password_change.html'

    def get(self, request, *args, **kwargs):
        form = StaticPasswordChangeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = StaticPasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            new_password_repeat = form.cleaned_data['new_password_repeat']
            if new_password != new_password_repeat:
                messages.error(request, "Le nuove password non coincidono.")
                return render(request, self.template_name, {'form': form})
            if not user.check_password(old_password):
                messages.error(request, "La vecchia password non è corretta.")
                return render(request, self.template_name, {'form': form})
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password modificata con successo.")
            return redirect('password_change')
        return render(request, self.template_name, {'form': form})
