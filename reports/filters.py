import django_filters
from sagragest.models import Order, Event, Daytime
from django.contrib.auth.models import Group
from django import forms
from django_filters.widgets import BooleanWidget

ACTIVE_CHOICES = (
    (True, 'Solo attivi'),
    (False, 'Tutti'),
)

class ReportFilter(django_filters.FilterSet):
    group = django_filters.ModelChoiceFilter(
        field_name='event__group', queryset=Group.objects.all(), label='Gruppo', required=False, empty_label="Tutti"
    )
    event = django_filters.ModelChoiceFilter(
        field_name='event', queryset=Event.objects.all(), label='Evento', required=False, empty_label="Tutti"
    )
    active_only = django_filters.BooleanFilter(
        field_name='event__active',
        label='Solo eventi attivi',
        widget=forms.CheckboxInput,
        required=False,
        method='filter_active_only'
    )
    daytime = django_filters.ModelChoiceFilter(
        field_name='daytime', queryset=Daytime.objects.all(), label='Giornata', required=False, empty_label="Tutti"
    )

    class Meta:
        model = Order
        fields = ['group', 'event', 'active_only', 'daytime']

    def filter_active_only(self, queryset, name, value):
        if value:
            return queryset.filter(event__active=True)
        return queryset

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        active_value = self.data.get('active_only')
        if active_value in ['on', True, 'true', 'True', 1, '1']:
            self.filters['event'].queryset = Event.objects.filter(active=True)
        else:
            self.filters['event'].queryset = Event.objects.all()
        if user and not user.is_superuser:
            user_groups = user.groups.all()
            if user_groups.exists():
                self.filters['group'].queryset = user_groups
                self.form.fields['group'].initial = user_groups.first().pk
                self.form.fields['group'].widget = forms.HiddenInput()
            else:
                self.form.fields['group'].widget = forms.HiddenInput()
