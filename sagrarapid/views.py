# Standard library
import io
import json
import openpyxl

# Django core
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.core.management import call_command
from django.db import models
from django import forms

# App imports
from sagragest.models import Event, CategoryEvent, CategoryTemplate, ProductTemplate, ProductEvent, Daytime, Order, OrderStatus, OrderItem
from sagragest.forms import EventForm, CategoryEventFromTemplateForm, CategoryCreateForm, CategoryEditForm, ProductCreateForm, ProductFromTemplateForm, ProductEditForm
from sagragest.resources import EventFullResource
from printers.utils import print_action
from core.utils import authenticated_required, admin_required
from sagragest.utils import import_event_xlsx
from sagrarapid.models import RapidInterface, RapidRows, RapidElements

# Third-party imports
from openpyxl import Workbook
from import_export.formats.base_formats import XLSX as XLSXFormat


from django.views.decorators.csrf import csrf_exempt

def get_events_for_user(user):
    if user.is_superuser:
        return Event.objects.all()
    elif user.is_staff:
        return Event.objects.filter(group__in=user.groups.all())
    return Event.objects.none()

@authenticated_required
def rapid_dashboard(request):
    events = get_events_for_user(request.user)
    if request.htmx:
        event_id = request.GET.get("event_id")
        interface = None
        event = None
        full_interface = None
        categoryevents = []
        productevents = []
        if event_id:
            try:
                event = Event.objects.get(pk=event_id)
                interface = RapidInterface.get_by_event(event)
                if interface:
                    full_interface = RapidInterface.objects.to_json_full_by_event(event)
                    categoryevents = CategoryEvent.objects.filter(event=event)
                    productevents = ProductEvent.objects.filter(event=event, category=interface.category_event)
            except Event.DoesNotExist:
                interface = None
        return render(request, "sagrarapid/dashboard.html#container", {
            "interface": interface,
            "event": event,
            "full_interface": full_interface,
            "categoryevents": categoryevents,
            "productevents": productevents,
        })
    return render(request, "sagrarapid/dashboard.html", {"events": events})

@authenticated_required
@require_POST
def rapid_move_row(request):
    row_id = request.POST.get('row_id')
    direction = request.POST.get('direction')  # 'up' o 'down'
    event_id = request.POST.get('event_id')
    row = get_object_or_404(RapidRows, id=row_id)
    interface = row.rapid_interface
    current_pos = row.row_position
    if direction == 'up' and current_pos > 0:
        new_pos = current_pos - 1
    elif direction == 'down':
        max_pos = interface.rapid_rows.count() - 1
        if current_pos < max_pos:
            new_pos = current_pos + 1
        else:
            new_pos = current_pos
    else:
        new_pos = current_pos
    interface.move_row(row, new_pos)
    # Ritorna la struttura richiesta
    interface_obj = None
    event = None
    full_interface = None
    categoryevents = []
    productevents = []
    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
            interface_obj = RapidInterface.get_by_event(event)
            if interface_obj:
                full_interface = RapidInterface.objects.to_json_full_by_event(event)
                categoryevents = CategoryEvent.objects.filter(event=event)
                productevents = ProductEvent.objects.filter(event=event, category=interface_obj.category_event)
        except Event.DoesNotExist:
            interface_obj = None
    return render(request, "sagrarapid/dashboard.html#container", {
        "interface": interface_obj,
        "event": event,
        "full_interface": full_interface,
        "categoryevents": categoryevents,
        "productevents": productevents,
    })

@authenticated_required
@require_POST
def rapid_move_element(request):
    element_id = request.POST.get('element_id')
    direction = request.POST.get('direction')  # 'up' o 'down'
    event_id = request.POST.get('event_id')
    element = get_object_or_404(RapidElements, id=element_id)
    row = element.rapid_row
    current_pos = element.position
    if direction == 'up' and current_pos > 0:
        new_pos = current_pos - 1
    elif direction == 'down':
        max_pos = row.elements.count() - 1
        if current_pos < max_pos:
            new_pos = current_pos + 1
        else:
            new_pos = current_pos
    else:
        new_pos = current_pos
    row.move_element(element, new_pos)
    # Ritorna la struttura richiesta
    interface_obj = None
    event = None
    full_interface = None
    categoryevents = []
    productevents = []
    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
            interface_obj = RapidInterface.get_by_event(event)
            if interface_obj:
                full_interface = RapidInterface.objects.to_json_full_by_event(event)
                categoryevents = CategoryEvent.objects.filter(event=event)
                productevents = ProductEvent.objects.filter(event=event, category=interface_obj.category_event)
        except Event.DoesNotExist:
            interface_obj = None
    return render(request, "sagrarapid/dashboard.html#container", {
        "interface": interface_obj,
        "event": event,
        "full_interface": full_interface,
        "categoryevents": categoryevents,
        "productevents": productevents,
    })

@require_POST
@authenticated_required
def rapid_add_element(request):
    row_id = request.POST.get('row_id')
    product_event_id = request.POST.get('product_event_id')
    event_id = request.POST.get('event_id')
    row = get_object_or_404(RapidRows, id=row_id)
    product_event = get_object_or_404(ProductEvent, id=product_event_id)
    # Trova la prima posizione libera nella riga
    max_pos = row.elements.count()
    elem = row.elements.create(product_event=product_event, position=max_pos)
    # Ritorna la struttura aggiornata come richiesto
    interface_obj = None
    event = None
    full_interface = None
    categoryevents = []
    productevents = []
    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
            interface_obj = RapidInterface.get_by_event(event)
            if interface_obj:
                full_interface = RapidInterface.objects.to_json_full_by_event(event)
                categoryevents = CategoryEvent.objects.filter(event=event)
                productevents = ProductEvent.objects.filter(event=event, category=interface_obj.category_event)
        except Event.DoesNotExist:
            interface_obj = None
    return render(request, "sagrarapid/dashboard.html#container", {
        "interface": interface_obj,
        "event": event,
        "full_interface": full_interface,
        "categoryevents": categoryevents,
        "productevents": productevents,
    })

@require_POST
@authenticated_required
def rapid_add_row(request):
    pass

@require_POST
@authenticated_required
def rapid_delete_row(request):
    row_id = request.POST.get('row_id')
    event_id = request.POST.get('event_id')
    row = get_object_or_404(RapidRows, id=row_id)
    interface = row.rapid_interface
    row.delete()
    # Ritorna la struttura richiesta
    interface_obj = None
    event = None
    full_interface = None
    categoryevents = []
    productevents = []
    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
            interface_obj = RapidInterface.get_by_event(event)
            if interface_obj:
                full_interface = RapidInterface.objects.to_json_full_by_event(event)
                categoryevents = CategoryEvent.objects.filter(event=event)
                productevents = ProductEvent.objects.filter(event=event, category=interface_obj.category_event)
        except Event.DoesNotExist:
            interface_obj = None
    return render(request, "sagrarapid/dashboard.html#container", {
        "interface": interface_obj,
        "event": event,
        "full_interface": full_interface,
        "categoryevents": categoryevents,
        "productevents": productevents,
    })

@require_POST
@authenticated_required
def rapid_delete_element(request):
    element_id = request.POST.get('element_id')
    event_id = request.POST.get('event_id')
    element = get_object_or_404(RapidElements, id=element_id)
    row = element.rapid_row
    element.delete()
    # Ritorna la struttura richiesta
    interface_obj = None
    event = None
    full_interface = None
    categoryevents = []
    productevents = []
    if event_id:
        try:
            event = Event.objects.get(pk=event_id)
            interface_obj = RapidInterface.get_by_event(event)
            if interface_obj:
                full_interface = RapidInterface.objects.to_json_full_by_event(event)
                categoryevents = CategoryEvent.objects.filter(event=event)
                productevents = ProductEvent.objects.filter(event=event, category=interface_obj.category_event)
        except Event.DoesNotExist:
            interface_obj = None
    return render(request, "sagrarapid/dashboard.html#container", {
        "interface": interface_obj,
        "event": event,
        "full_interface": full_interface,
        "categoryevents": categoryevents,
        "productevents": productevents,
    })

@require_POST
@authenticated_required
def rapid_change_category(request):
    form = request.POST.get('form')
    category_id = request.POST.get('category_id')
    event_id = request.POST.get('event_id')
    if form == 'true':
        # Filtra le categorie per l'evento e rimuovi quella selezionata (se presente)
        categoryevents = []
        event = None
        if event_id:
            try:
                event = Event.objects.get(pk=event_id)
                categoryevents = list(CategoryEvent.objects.filter(event=event))
                if category_id:
                    categoryevents = [cat for cat in categoryevents if str(cat.id) != str(category_id)]
            except Event.DoesNotExist:
                categoryevents = []
        return render(request, "sagrarapid/dashboard.html#category-form", {"categoryevents": categoryevents, "event": event})
    category = get_object_or_404(CategoryEvent, id=category_id)
    interface = RapidInterface.get_by_event(category.event)
    if interface:
        interface.category_event = category
        interface.save()
        # Ritorna la struttura richiesta
        interface_obj = None
        event = None
        full_interface = None
        categoryevents = []
        productevents = []
        if event_id:
            try:
                event = Event.objects.get(pk=event_id)
                interface_obj = RapidInterface.get_by_event(event)
                if interface_obj:
                    full_interface = RapidInterface.objects.to_json_full_by_event(event)
                    categoryevents = CategoryEvent.objects.filter(event=event)
                    productevents = ProductEvent.objects.filter(event=event, category=interface_obj.category_event)
            except Event.DoesNotExist:
                interface_obj = None
        return render(request, "sagrarapid/dashboard.html#container", {
            "interface": interface_obj,
            "event": event,
            "full_interface": full_interface,
            "categoryevents": categoryevents,
            "productevents": productevents,
        })
    return HttpResponseForbidden("Interfaccia non trovata")

@authenticated_required
def rapid_order_entry(request):
    """
    Pagina di inserimento ordine rapido robusta:
    - Selezione evento/giornata attiva visibile all'utente
    - Gestione errori se non ci sono eventi/giornate attive
    - Passaggio daytimes, selected_daytime, interface, full_interface
    - POST: salva ordine rapido con campi preimpostati
    """
    from sagragest.models import Event, Daytime, Order, OrderItem, ProductEvent
    user = request.user
    # Recupera eventi attivi visibili all'utente
    if user.is_superuser:
        events = Event.objects.filter(active=True)
    else:
        events = Event.objects.filter(active=True, group__in=user.groups.all())
    if not events.exists():
        return render(request, "sagragest/order_entry_no_daytime.html", {"options": "event"})
    # Recupera la giornata attiva tra quegli eventi
    active_daytime = Daytime.objects.filter(end__isnull=True, event__in=events).first()
    if not active_daytime:
        return render(request, "sagragest/order_entry_no_daytime.html", {"options": "daytime"})
    # Giornate visibili all'utente
    if user.is_superuser:
        daytimes = Daytime.objects.filter(end__isnull=True, event__in=events)
    else:
        daytimes = [active_daytime]
    # Selezione giornata (da GET) o giornata attiva di default
    selected_daytime_id = request.GET.get("daytime_id")
    if selected_daytime_id:
        selected_daytime = Daytime.objects.filter(pk=selected_daytime_id).first()
        if not selected_daytime:
            selected_daytime = active_daytime
    else:
        selected_daytime = active_daytime
    event = selected_daytime.event
    # Interfaccia rapida
    interface = RapidInterface.get_by_event(event)
    full_interface = RapidInterface.objects.to_json_full_by_event(event) if interface else None
    if request.method == 'POST':
        prodotti = request.POST.getlist('prodotti[]')
        quantities = request.POST.getlist('quantities[]')
        numero = Order.get_next_number_for_daytime(selected_daytime)
        ordine = Order.objects.create(
            number=numero,
            daytime=selected_daytime,
            event=event,
            status='ORDERED',
            table_number=0,
            cover=0,
            is_takeaway=True,
            created_by=request.user,
            client='',
            extra_price=0.0,
        )
        totale = 0
        for prod_id, qty in zip(prodotti, quantities):
            try:
                prod_ev = ProductEvent.objects.get(pk=prod_id)
                qty = int(qty)
                item = OrderItem.objects.create(
                    order=ordine,
                    product_event=prod_ev,
                    quantity=qty,
                    price_at_order_time=prod_ev.price,
                )
                totale += prod_ev.price * qty
            except Exception:
                continue
        ordine.total = totale
        ordine.save()
        messages.success(request, 'Ordine rapido inserito correttamente!')
        print_action(ordine, "PRINT_FOR_ALL")
        print(f"[BACKEND] Ordine #{{order.number}} creato per giornata {{daytime.id}} e evento '{{daytime.event.name}}'.")
        return redirect('rapid-order')
    context = {
        'events': events,
        'daytimes': daytimes,
        'selected_daytime': selected_daytime,
        'event': event,
        'interface': interface,
        'full_interface': full_interface,
    }
    return render(request, 'sagrarapid/order_entry.html', context)