from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from printers.utils import get_cups_printers
from allauth.account.forms import SignupForm

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    personal_printer = forms.ChoiceField(
        label="Stampante personale",
        required=False,
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        printers = get_cups_printers()
        self.fields['personal_printer'].choices = [('', '--- Nessuna ---')] + [(p, p) for p in printers]

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'theme', 'personal_printer']

class CustomSignupForm(SignupForm):
    theme = forms.ChoiceField(choices=User._meta.get_field('theme').choices, label="Tema grafico", required=False)
    personal_printer = forms.CharField(max_length=100, required=False, label="Stampante personale")
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Gruppo")

    def save(self, request):
        user = super().save(request)
        user.theme = self.cleaned_data.get('theme', 'light')
        user.personal_printer = self.cleaned_data.get('personal_printer', '')
        user.save()
        group = self.cleaned_data.get('group')
        if group:
            user.groups.set([group])
        return user

class StaticPasswordResetForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)

class StaticPasswordChangeForm(forms.Form):
    old_password = forms.CharField(label="Vecchia password", widget=forms.PasswordInput)
    new_password = forms.CharField(label="Nuova password", widget=forms.PasswordInput)
    new_password_repeat = forms.CharField(label="Ripeti nuova password", widget=forms.PasswordInput)
