from .models import Event, CategoryEvent, CategoryTemplate, ProductTemplate, ProductEvent
from django import forms

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'year', 'active', 'group', 'option_client', 'option_table', 'option_cover', 'pay_cover', 'pay_takeaway']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full'}),
            'year': forms.NumberInput(attrs={'class': 'input input-bordered w-full'}),
            'active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'group': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'option_client': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'option_table': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'option_cover': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'pay_cover': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
            'pay_takeaway': forms.NumberInput(attrs={'class': 'input input-bordered w-full', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if not user or not user.is_superuser:
            self.fields.pop("group")

    def clean(self):
        cleaned_data = super().clean()
        option_client = cleaned_data.get('option_client')
        option_table = cleaned_data.get('option_table')
        option_cover = cleaned_data.get('option_cover')
        if not (option_client or option_table or option_cover):
            raise forms.ValidationError(
                "Devi selezionare almeno una tra le opzioni: Cliente, Tavolo o Coperto.")
        return cleaned_data
            
class CategoryEventFromTemplateForm(forms.Form):
    category_template = forms.ModelChoiceField(
        queryset=CategoryTemplate.objects.none(),
        label="Categoria da Template",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    display_order = forms.ChoiceField(
        label="Ordine di Visualizzazione",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    display_elements = forms.IntegerField(
        label="Elementi da Visualizzare",
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"})
    )

    def __init__(self, *args, **kwargs):
        event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)

        if event:
            used_orders = set(CategoryEvent.objects.filter(event=event).values_list("display_order", flat=True))
            available_orders = []
            i = 0
            while len(available_orders) < 5:
                if i not in used_orders:
                    available_orders.append(i)
                i += 1

            self.fields["display_order"].choices = [(i, str(i)) for i in available_orders]

            used_templates = CategoryEvent.objects.filter(event=event).values_list("category_id", flat=True)
            self.fields["category_template"].queryset = CategoryTemplate.objects.exclude(id__in=used_templates)

class CategoryCreateForm(forms.ModelForm):
    display_order = forms.ChoiceField(
        label="Ordine di Visualizzazione",
        widget=forms.Select(attrs={'class': 'select select-bordered w-full'})
    )
    display_elements = forms.IntegerField(
        label="Elementi da Visualizzare",
        widget=forms.NumberInput(attrs={'class': 'input input-bordered w-full'})
    )

    class Meta:
        model = CategoryTemplate
        fields = ['name', 'description']
        labels = {
            'name': 'Nome Categoria',
            'description': 'Descrizione',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Es. Primi Piatti',
            }),
            'description': forms.TextInput(attrs={  # ← qui il cambiamento
                'class': 'input input-bordered w-full',
                'placeholder': 'Descrizione della categoria',
            }),
        }

    def __init__(self, *args, **kwargs):
        event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)

        if event:
            used_orders = set(CategoryEvent.objects.filter(event=event).values_list("display_order", flat=True))
            available_orders = []
            i = 0
            while len(available_orders) < 10:
                if i not in used_orders:
                    available_orders.append(i)
                i += 1

            self.fields["display_order"].choices = [(i, str(i)) for i in available_orders]

    def clean_name(self):
        name = self.cleaned_data['name']
        if CategoryTemplate.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Esiste già una categoria con questo nome.")
        return name

class CategoryEditForm(forms.ModelForm):
    display_order = forms.ChoiceField(
        label="Ordine di Visualizzazione",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    display_elements = forms.IntegerField(
        label="Elementi da Visualizzare",
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"})
    )

    class Meta:
        model = CategoryEvent
        fields = ["display_order", "display_elements"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        if instance:
            event = instance.event
            used_orders = set(
                CategoryEvent.objects.filter(event=event).exclude(pk=instance.pk).values_list("display_order", flat=True)
            )
            available_orders = []
            i = 0
            while len(available_orders) < 5:
                if i not in used_orders:
                    available_orders.append(i)
                i += 1

            if instance.display_order not in available_orders:
                available_orders.append(instance.display_order)
                available_orders.sort()

            self.fields["display_order"].choices = [(i, str(i)) for i in available_orders]
            self.fields["display_order"].initial = instance.display_order

class ProductCreateForm(forms.ModelForm):
    price = forms.DecimalField(
        label="Prezzo",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"})
    )
    display_order = forms.ChoiceField(
        label="Ordine visualizzazione",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    category_event = forms.ModelChoiceField(
        queryset=CategoryEvent.objects.all(),
        widget=forms.HiddenInput()
    )

    class Meta:
        model = ProductTemplate
        fields = ["name", "description"]
        labels = {
            "name": "Nome Prodotto",
            "description": "Descrizione Prodotto",
        }
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "input input-bordered w-full",
                "placeholder": "Es. Pizza Margherita",
            }),
            "description": forms.TextInput(attrs={  # ← qui il cambiamento
                'class': 'input input-bordered w-full',
                'placeholder': 'Descrizione Prodotto',
            }),
        }

    def __init__(self, *args, **kwargs):
        category_event = kwargs.pop("category_event", None)
        super().__init__(*args, **kwargs)
        if category_event:
            self.fields["category_event"].initial = category_event
            self.fields["category_event"].queryset = CategoryEvent.objects.filter(pk=category_event.pk)

            used_orders = set(ProductEvent.objects.filter(category=category_event).values_list("display_order", flat=True))
            available_orders = []
            i = 0
            while len(available_orders) < 5:
                if i not in used_orders:
                    available_orders.append(i)
                i += 1
            self.fields["display_order"].choices = [(i, str(i)) for i in available_orders]


class ProductFromTemplateForm(forms.Form):
    template = forms.ModelChoiceField(
        queryset=ProductTemplate.objects.all(),
        label="Prodotto Template",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    price = forms.DecimalField(
        label="Prezzo personalizzato",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full"})
    )
    display_order = forms.ChoiceField(
        label="Ordine visualizzazione",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )
    category_event = forms.ModelChoiceField(queryset=CategoryEvent.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        category_event = kwargs.pop("category_event", None)
        super().__init__(*args, **kwargs)
        if category_event:
            self.fields["category_event"].initial = category_event
            self.fields["category_event"].queryset = CategoryEvent.objects.filter(pk=category_event.pk)

            used = set(ProductEvent.objects.filter(category=category_event).values_list("display_order", flat=True))
            available_orders = []
            i = 0
            while len(available_orders) < 5:
                if i not in used:
                    available_orders.append(i)
                i += 1

            self.fields["display_order"].choices = [(i, str(i)) for i in available_orders]

class ProductEditForm(forms.ModelForm):
    display_order = forms.ChoiceField(
        label="Ordine visualizzazione",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"})
    )

    class Meta:
        model = ProductEvent
        fields = ["price", "display_order"]
        widgets = {
            "price": forms.NumberInput(attrs={"class": "input input-bordered w-full"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            category_event = instance.category
            used_orders = set(
                ProductEvent.objects.filter(category=category_event).exclude(pk=instance.pk).values_list("display_order", flat=True)
            )
            available_orders = []
            i = 0
            while len(available_orders) < 5:
                if i not in used_orders:
                    available_orders.append(i)
                i += 1
            if instance.display_order not in available_orders:
                available_orders.append(instance.display_order)
                available_orders.sort()
            self.fields["display_order"].choices = [(i, str(i)) for i in available_orders]
            self.fields["display_order"].initial = instance.display_order