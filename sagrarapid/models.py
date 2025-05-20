from django.db import models
from sagragest.models import Event, CategoryEvent, ProductEvent

class RapidInterfaceManager(models.Manager):
    def create_interface_with_rows_and_elements(self, event, category_event, rows_elements):
        # Crea una sola RapidInterface per evento e category_event
        interface, created = self.get_or_create(event=event, category_event=category_event)
        for row_elements in rows_elements:
            # Trova la prima posizione libera per la riga
            used_row_positions = set(interface.rapid_rows.values_list('row_position', flat=True))
            row_position = 0
            while row_position in used_row_positions:
                row_position += 1
            # Crea la RapidRow
            rapid_row = interface.rapid_rows.create(row_position=row_position)
            for product_event_id in row_elements:
                # Verifica che il ProductEvent sia della category_event e dell'evento
                try:
                    product_event = ProductEvent.objects.get(id=product_event_id, category=category_event, event=event)
                except ProductEvent.DoesNotExist:
                    continue
                # Trova la prima posizione libera per l'elemento nella riga
                used_elem_positions = set(rapid_row.elements.values_list('position', flat=True))
                elem_position = 0
                while elem_position in used_elem_positions:
                    elem_position += 1
                # Crea RapidElements
                elem = RapidElements.objects.create(product_event=product_event, position=elem_position)
                rapid_row.elements.add(elem)
                rapid_row.save()
        return interface

    def delete_interface_and_related(self, interface):
        # Elimina tutte le RapidRows e RapidElements collegati a questa interfaccia
        for row in interface.rapid_rows.all():
            row.delete_row_and_update_positions()
        interface.delete()

    def change_category(self, interface, new_category_event):
        # Elimina tutte le righe e gli elementi collegati (ma non Event, CategoryEvent, ProductEvent)
        for row in interface.rapid_rows.all():
            row.delete_row_and_update_positions()
        interface.category_event = new_category_event
        interface.save()

    def get_full_by_event(self, event):
        """
        Restituisce la RapidInterface associata a un evento, con tutte le RapidRows e RapidElements collegati.
        Ritorna un dizionario con la struttura:
        {
            'interface': RapidInterface,
            'rows': [
                {
                    'row': RapidRows,
                    'elements': [RapidElements, ...]
                },
                ...
            ]
        }
        """
        interface = self.filter(event=event).first()
        if not interface:
            return None
        rows_data = []
        rows = interface.rapid_rows.order_by('row_position')
        for row in rows:
            elements = row.elements.order_by('position')
            rows_data.append({
                'row': row,
                'elements': list(elements)
            })
        return {
            'interface': interface,
            'rows': rows_data
        }

    def to_json_full_by_event(self, event):
        """
        Restituisce una struttura completamente serializzabile in JSON per l'interfaccia rapida di un evento.
        """
        data = self.get_full_by_event(event)
        if not data:
            return None
        interface = data['interface']
        rows = data['rows']
        return {
            'interface': {
                'id': interface.id,
                'event_id': interface.event_id,
                'category_event_id': interface.category_event_id,
                'event_name': interface.event.name,
                'category_name': interface.category_event.category.name,
            },
            'rows': [
                {
                    'row_id': row_data['row'].id,
                    'row_position': row_data['row'].row_position,
                    'elements': [
                        {
                            'element_id': elem.id,
                            'product_event_id': elem.product_event.id,
                            'product_name': elem.product_event.product.name,
                            'position': elem.position,
                            'price': float(elem.product_event.price),
                        }
                        for elem in row_data['elements']
                    ]
                }
                for row_data in rows
            ]
        }

class RapidInterface(models.Model):
    class Meta:
        verbose_name = "Interfaccia Rapida"
        verbose_name_plural = "Interfacce Rapide"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rapid_interfaces", verbose_name="Evento")
    category_event = models.ForeignKey(CategoryEvent, on_delete=models.CASCADE, related_name="rapid_interfaces", verbose_name="Categoria Evento")

    objects = RapidInterfaceManager()

    @classmethod
    def get_by_event(cls, event):
        """Restituisce la RapidInterface associata a un evento, oppure None se non esiste."""
        return cls.objects.filter(event=event).first()

    def __str__(self):
        return f"{self.event.name} - {self.category_event.category.name}"

    def move_row(self, row, new_position):
        rows = list(self.rapid_rows.order_by('row_position'))
        old_position = row.row_position
        if old_position == new_position:
            return
        if new_position < 0:
            new_position = 0
        max_position = len(rows) - 1
        if new_position > max_position:
            new_position = max_position
        if new_position < old_position:
            # Spostamento verso l'alto: incrementa di 1 tutte tra new_position e old_position-1
            self.rapid_rows.filter(row_position__gte=new_position, row_position__lt=old_position).update(row_position=models.F('row_position') + 1)
        else:
            # Spostamento verso il basso: decrementa di 1 tutte tra old_position+1 e new_position
            self.rapid_rows.filter(row_position__gt=old_position, row_position__lte=new_position).update(row_position=models.F('row_position') - 1)
        row.row_position = new_position
        row.save()
        # Risincronizza le posizioni per garantire che siano 0..n-1 senza buchi
        for idx, r in enumerate(self.rapid_rows.order_by('row_position')):
            if r.row_position != idx:
                r.row_position = idx
                r.save()

class RapidElements(models.Model):
    class Meta:
        verbose_name = "Elemento Rapido"
        verbose_name_plural = "Elementi Rapidi"

    product_event = models.ForeignKey(ProductEvent, on_delete=models.CASCADE, related_name="rapid_elements", verbose_name="Prodotto Evento")
    position = models.IntegerField(verbose_name="Posizione nella riga")
    rapid_row = models.ForeignKey('RapidRows', on_delete=models.CASCADE, related_name="elements", verbose_name="Riga Rapida", null=True, blank=True)

    def __str__(self):
        return f"{self.product_event.product.name} (pos {self.position})"

    def delete_element_and_update_positions(self):
        row = self.rapid_row
        my_position = self.position
        self.delete()
        # Scala le posizioni degli elementi successivi nella riga
        if row:
            for elem in row.elements.filter(position__gt=my_position):
                elem.position -= 1
                elem.save()

    def change_product(self, new_product_event):
        # Verifica che il nuovo prodotto sia della stessa categoria_event e event
        row = self.rapid_row
        if row and new_product_event.category == row.rapid_interface.category_event and new_product_event.event == row.rapid_interface.event:
            self.product_event = new_product_event
            self.save()
        else:
            raise ValueError("Prodotto non valido per questa categoria/evento")

class RapidRows(models.Model):
    class Meta:
        verbose_name = "Riga Rapida"
        verbose_name_plural = "Righe Rapide"

    rapid_interface = models.ForeignKey(RapidInterface, on_delete=models.CASCADE, related_name="rapid_rows", verbose_name="Interfaccia Rapida")
    row_position = models.IntegerField(verbose_name="Posizione della riga")

    def __str__(self):
        return f"{self.rapid_interface} (riga {self.row_position})"

    def delete_row_and_update_positions(self):
        interface = self.rapid_interface
        my_position = self.row_position
        # Elimina tutti gli elementi associati a questa riga
        for elem in self.elements.all():
            elem.delete()
        self.delete()
        # Scala le posizioni delle righe successive
        for row in interface.rapid_rows.filter(row_position__gt=my_position):
            row.row_position -= 1
            row.save()

    def move_element(self, element, new_position):
        elements = list(self.elements.order_by('position'))
        old_position = element.position
        if old_position == new_position:
            return
        if new_position < 0:
            new_position = 0
        max_position = len(elements) - 1
        if new_position > max_position:
            new_position = max_position
        if new_position < old_position:
            # Spostamento verso l'alto: incrementa di 1 tutti tra new_position e old_position-1
            self.elements.filter(position__gte=new_position, position__lt=old_position).update(position=models.F('position') + 1)
        else:
            # Spostamento verso il basso: decrementa di 1 tutti tra old_position+1 e new_position
            self.elements.filter(position__gt=old_position, position__lte=new_position).update(position=models.F('position') - 1)
        element.position = new_position
        element.save()
        # Risincronizza le posizioni per garantire che siano 0..n-1 senza buchi
        for idx, elem in enumerate(self.elements.order_by('position')):
            if elem.position != idx:
                elem.position = idx
                elem.save()

