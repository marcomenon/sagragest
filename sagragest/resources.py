from tablib import Dataset
from django.utils.timezone import is_aware
from import_export import resources, fields
from .models import Event, CategoryEvent, ProductEvent, Daytime, Order, OrderItem, CategoryTemplate, ProductTemplate

class CategoryTemplateResource(resources.ModelResource):
    class Meta:
        model = CategoryTemplate
        fields = ("id", "name", "description")

class ProductTemplateResource(resources.ModelResource):
    class Meta:
        model = ProductTemplate
        fields = ("id", "name", "description")

class CategoryEventResource(resources.ModelResource):
    class Meta:
        model = CategoryEvent
        fields = ("id", "event", "category", "display_order", "display_elements")

class ProductEventResource(resources.ModelResource):
    class Meta:
        model = ProductEvent
        fields = ("id", "event", "product", "category", "price", "display_order")

class DaytimeResource(resources.ModelResource):
    class Meta:
        model = Daytime
        fields = ("id", "start", "end", "event", "note")

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        fields = ("id", "number", "daytime", "event", "created_at", "closed_at", "status", "notes", "total", "table_number", "cover", "is_takeaway", "created_by", "client", "extra_price")

class OrderItemResource(resources.ModelResource):
    class Meta:
        model = OrderItem
        fields = ("id", "order", "product_event", "quantity", "note", "price_at_order_time", "total_price")

class EventFullResource(resources.ModelResource):
    class Meta:
        model = Event
        fields = ("id", "name", "year", "active", "group", "option_client", "option_table", "option_cover", "pay_cover", "pay_takeaway")

    def export_event_full(self, event):
        """
        Esporta tutti i dati collegati a un evento in un dict di dataset (uno per modello),
        usando logical_id per tutte le FK.
        """
        def dt_to_str(dt):
            if not dt:
                return ""
            if is_aware(dt):
                dt = dt.replace(tzinfo=None)
            return dt.isoformat(sep=" ")
        # Logical ID mapping
        ct_map = {}
        pt_map = {}
        ce_map = {}
        pe_map = {}
        dt_map = {}
        o_map = {}
        oi_map = {}
        ct_counter = pt_counter = ce_counter = pe_counter = dt_counter = o_counter = oi_counter = 1
        # CategoryTemplate
        ct_ds = Dataset(headers=["logical_id", "name", "description"])
        for ct in CategoryTemplate.objects.filter(event_links__event=event).distinct():
            logical_id = f"CT{ct_counter}"
            ct_map[ct.id] = logical_id
            ct_ds.append([logical_id, ct.name, ct.description])
            ct_counter += 1
        # ProductTemplate
        pt_ds = Dataset(headers=["logical_id", "name", "description"])
        for pt in ProductTemplate.objects.filter(event_links__event=event).distinct():
            logical_id = f"PT{pt_counter}"
            pt_map[pt.id] = logical_id
            pt_ds.append([logical_id, pt.name, pt.description])
            pt_counter += 1
        # CategoryEvent
        ce_ds = Dataset(headers=["logical_id", "event", "category", "display_order", "display_elements"])
        for ce in CategoryEvent.objects.filter(event=event):
            logical_id = f"CE{ce_counter}"
            ce_map[ce.id] = logical_id
            ce_ds.append([
                logical_id,
                event.id,  # event è unico
                ct_map.get(ce.category_id),
                ce.display_order,
                ce.display_elements
            ])
            ce_counter += 1
        # ProductEvent
        pe_ds = Dataset(headers=["logical_id", "event", "product", "category", "price", "display_order"])
        for pe in ProductEvent.objects.filter(event=event):
            logical_id = f"PE{pe_counter}"
            pe_map[pe.id] = logical_id
            pe_ds.append([
                logical_id,
                event.id,
                pt_map.get(pe.product_id),
                ce_map.get(pe.category_id),
                pe.price,
                pe.display_order
            ])
            pe_counter += 1
        # Daytime
        dt_ds = Dataset(headers=["logical_id", "start", "end", "event", "note"])
        for dt in Daytime.objects.filter(event=event):
            logical_id = f"DT{dt_counter}"
            dt_map[dt.id] = logical_id
            dt_ds.append([
                logical_id,
                dt_to_str(dt.start),
                dt_to_str(dt.end),
                event.id,
                dt.note
            ])
            dt_counter += 1
        # Order
        o_ds = Dataset(headers=["logical_id", "number", "daytime", "event", "created_at", "closed_at", "status", "notes", "total", "table_number", "cover", "is_takeaway", "client", "extra_price"])
        for o in Order.objects.filter(event=event):
            logical_id = f"O{o_counter}"
            o_map[o.id] = logical_id
            o_ds.append([
                logical_id,
                o.number,
                dt_map.get(o.daytime_id),
                event.id,
                dt_to_str(o.created_at),
                dt_to_str(o.closed_at),
                o.status,
                o.notes,
                o.total,
                o.table_number,
                o.cover,
                o.is_takeaway,
                o.client,
                o.extra_price
            ])
            o_counter += 1
        # OrderItem
        oi_ds = Dataset(headers=["logical_id", "order", "product_event", "quantity", "note", "price_at_order_time", "total_price"])
        for oi in OrderItem.objects.filter(order__event=event):
            logical_id = f"OI{oi_counter}"
            oi_map[oi.id] = logical_id
            oi_ds.append([
                logical_id,
                o_map.get(oi.order_id),
                pe_map.get(oi.product_event_id),
                oi.quantity,
                oi.note,
                oi.price_at_order_time,
                oi.total_price
            ])
            oi_counter += 1
        # Event (singolo)
        event_ds = Dataset(headers=["id", "name", "year", "active", "group", "option_client", "option_table", "option_cover", "pay_cover", "pay_takeaway"])
        event_ds.append([
            event.id, event.name, event.year, event.active, event.group_id, event.option_client, event.option_table, event.option_cover, event.pay_cover, event.pay_takeaway
        ])
        return {
            "Event": event_ds,
            "CategoryTemplate": ct_ds,
            "ProductTemplate": pt_ds,
            "CategoryEvent": ce_ds,
            "ProductEvent": pe_ds,
            "Daytime": dt_ds,
            "Order": o_ds,
            "OrderItem": oi_ds,
        }
