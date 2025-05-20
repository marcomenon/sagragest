from django.core.management.base import BaseCommand, CommandError
from sagragest.models import Event, CategoryTemplate, ProductTemplate, CategoryEvent, ProductEvent


class Command(BaseCommand):
    help = 'Clona categorie e prodotti da un evento esistente a uno nuovo'

    def add_arguments(self, parser):
        parser.add_argument('source_event_id', type=int, help="ID dell'evento sorgente")
        parser.add_argument('target_event_id', type=int, help="ID dell'evento di destinazione")

    def handle(self, *args, **options):
        source_event_id = options['source_event_id']
        target_event_id = options['target_event_id']

        try:
            source_event = Event.objects.get(pk=source_event_id)
            target_event = Event.objects.get(pk=target_event_id)
        except Event.DoesNotExist:
            raise CommandError('Evento non trovato.')

        self.stdout.write(self.style.NOTICE(f"Clonazione da '{source_event}' a '{target_event}'"))

        # Mappa per evitare duplicazioni inutili
        category_map = {}

        # Clona CategoryEvent
        for cat_event in CategoryEvent.objects.filter(event=source_event):
            new_cat_event = CategoryEvent.objects.create(
                event=target_event,
                category=cat_event.category,
                display_order=cat_event.display_order,
                display_elements=cat_event.display_elements,
            )
            category_map[cat_event.id] = new_cat_event

        self.stdout.write(self.style.SUCCESS(f"Clonate {len(category_map)} categorie."))

        # Clona ProductEvent
        count_products = 0
        for prod_event in ProductEvent.objects.filter(event=source_event):
            old_cat_event = prod_event.category
            new_cat_event = category_map.get(old_cat_event.id)

            if not new_cat_event:
                continue  # Skip prodotti collegati a categorie non trovate

            ProductEvent.objects.create(
                event=target_event,
                product=prod_event.product,
                category=new_cat_event,
                price=prod_event.price,
                display_order=prod_event.display_order
            )
            count_products += 1

        self.stdout.write(self.style.SUCCESS(f"Clonati {count_products} prodotti."))
