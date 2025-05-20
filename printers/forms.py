from django import forms
from .models import PrinterLayout
from django.core.exceptions import ValidationError
from sagragest.models import CategoryEvent
from .utils import get_cups_printers

class PrinterLayoutForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=CategoryEvent.objects.none(),
        required=False,
        label="Categorie associate",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox checkbox-primary'})
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        if 'layout_path' in self.fields:
            self.fields['layout_path'].widget = forms.HiddenInput()
            self.fields['layout_path'].required = False
        # Recupero tutte le stampanti CUPS
        all_cups_printers = get_cups_printers()
        # Pulizia: rimosso used_printers, non più utilizzato
        if event:
            event_id = event
        else:
            event_id = self.data.get('event') or self.initial.get('event') or (self.instance.event.pk if self.instance and self.instance.event else None)
        if event_id:
            self.fields['category'].queryset = CategoryEvent.objects.filter(event=event_id)
        else:
            self.fields['category'].queryset = CategoryEvent.objects.none()
        available = [(p, p) for p in all_cups_printers]
        self.fields['printer'] = forms.ChoiceField(
            choices=[('', '---------')] + available,
            required=False,
            label='Stampante',
            widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
        )
        if self.instance.pk:
            self.fields['category'].initial = self.instance.category.all()

    def clean(self):
        cleaned_data = super().clean()
        is_user = cleaned_data.get('is_user')
        event = cleaned_data.get('event')
        printer = cleaned_data.get('printer')
        name = cleaned_data.get('name')
        qs = PrinterLayout.objects.filter(event=event)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if is_user:
            if qs.filter(is_user=True, printer__isnull=True).exists() and not (self.instance and self.instance.is_user and not self.instance.printer):
                raise ValidationError("Per ogni evento può esserci solo un layout utente (is_user=True) e senza stampante associata.")
            if printer:
                raise ValidationError("Un layout utente non può avere una stampante associata.")
        else:
            if not printer:
                raise ValidationError("Un layout non utente deve avere una stampante associata.")
        return cleaned_data

    class Meta:
        model = PrinterLayout
        fields = ['name', 'printer', 'layout_path', 'is_user', 'event', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'is_user': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'event': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'printer': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
        }
