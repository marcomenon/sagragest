import django_filters
from sagragest.models import Order, Event, Daytime
from django.contrib.auth.models import Group
from django import forms

class ReportFilter(django_filters.FilterSet):
    group = django_filters.ModelChoiceFilter(
        field_name='event__group', queryset=Group.objects.none(), label='Gruppo', required=False, empty_label="Tutti"
    )
    event = django_filters.ModelChoiceFilter(
        field_name='event', queryset=Event.objects.none(), label='Evento', required=False, empty_label="Tutti"
    )
    active_only = django_filters.BooleanFilter(
        field_name='event__active',
        label='Solo eventi attivi',
        widget=forms.CheckboxInput,
        required=False,
        method='filter_active_only'
    )
    daytime = django_filters.ModelChoiceFilter(
        field_name='daytime', queryset=Daytime.objects.none(), label='Giornata', required=False, empty_label="Tutti"
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
        active_value = None
        if 'data' in kwargs and kwargs['data']:
            active_value = kwargs['data'].get('active_only')
        # Imposta i queryset PRIMA di chiamare super().__init__
        if user and not user.is_superuser:
            user_groups = user.groups.all()
            if user_groups.exists():
                self.base_filters['group'].queryset = user_groups
                event_qs = Event.objects.filter(group__in=user_groups)
                if active_value in ['on', True, 'true', 'True', 1, '1']:
                    event_qs = event_qs.filter(active=True)
                self.base_filters['event'].queryset = event_qs
                self.base_filters['daytime'].queryset = Daytime.objects.filter(event__group__in=user_groups).distinct()
            else:
                self.base_filters['group'].queryset = Group.objects.none()
                self.base_filters['event'].queryset = Event.objects.none()
                self.base_filters['daytime'].queryset = Daytime.objects.none()
        else:
            if active_value in ['on', True, 'true', 'True', 1, '1']:
                self.base_filters['event'].queryset = Event.objects.filter(active=True)
            else:
                self.base_filters['event'].queryset = Event.objects.all()
            self.base_filters['group'].queryset = Group.objects.all()
            self.base_filters['daytime'].queryset = Daytime.objects.all()

        super().__init__(*args, **kwargs)

        # --- Dipendenza Event da Group selezionato ---
        selected_group = self.data.get('group')
        if selected_group:
            try:
                selected_group = int(selected_group)
                self.filters['event'].queryset = self.filters['event'].queryset.filter(group_id=selected_group)
            except (ValueError, TypeError):
                pass

        # --- Dipendenza Daytime da Event selezionato ---
        selected_event = self.data.get('event')
        if selected_event:
            try:
                selected_event = int(selected_event)
                self.filters['daytime'].queryset = Daytime.objects.filter(event_id=selected_event)
            except (ValueError, TypeError):
                pass
