from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import PrinterLayout
from sagragest.models import Event
from .forms import PrinterLayoutForm
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from core.utils import admin_required

@admin_required
def printlayout_list(request):
    # Recupera tutti gli eventi visibili all'utente
    if request.user.is_superuser:
        events = Event.objects.all()
        layouts = PrinterLayout.objects.all()
    else:
        events = Event.objects.filter(group__in=request.user.groups.all(), active=True)
        layouts = PrinterLayout.objects.filter(event__in=events)
    # Associa a ogni evento la lista dei layout (anche vuota)
    event_layouts = []
    layouts_by_event = {}
    for layout in layouts.select_related('event'):
        layouts_by_event.setdefault(layout.event_id, []).append(layout)
    for event in events.order_by('year', 'name'):
        event_layouts.append((event, layouts_by_event.get(event.id, [])))
    if request.htmx:
        return render(request, "printers/printers.html#printlayout_list", {"event_layouts": event_layouts})
    return render(request, "printers/printers.html", {"event_layouts": event_layouts})

@admin_required
def printlayout_create(request):
    if request.method == "POST":
        form = PrinterLayoutForm(request.POST, user=request.user)
        if form.is_valid():
            layout = form.save(commit=False)
            layout.save()
            form.save_m2m()  # Salva le categorie associate
            return HttpResponse("", headers={"HX-Trigger": "refreshPrintlayoutList"})
    else:
        form = PrinterLayoutForm(user=request.user)
    return render(request, "printers/printers.html#printlayout_form", {"form": form, "action": reverse('printers:printlayout_create')})

@admin_required
def printlayout_update(request, pk):
    layout = get_object_or_404(PrinterLayout, pk=pk)
    if request.method == "POST":
        form = PrinterLayoutForm(request.POST, instance=layout, user=request.user)
        if form.is_valid():
            layout = form.save(commit=False)
            layout.save()
            form.save_m2m()  # Salva le categorie associate
            return HttpResponse("", headers={"HX-Trigger": "refreshPrintlayoutList"})
    else:
        form = PrinterLayoutForm(instance=layout, user=request.user)
    return render(request, "printers/printers.html#printlayout_form", {"form": form, "action": reverse('printers:printlayout_update', args=[pk])})

@admin_required
@require_POST
def printlayout_delete(request, pk):
    layout = get_object_or_404(PrinterLayout, pk=pk)
    event = layout.event
    layout.delete()
    # Recupera solo i layout dell'evento interessato
    layouts = PrinterLayout.objects.filter(event=event)
    event_layouts = [(event, list(layouts))]
    return render(request, "printers/printers.html#printlayout_list", {"event_layouts": event_layouts})

@admin_required
def printlayout_form(request):
    event_id = request.GET.get('event_id')
    action_type = request.GET.get('action', 'create')
    initial = {}
    if event_id:
        initial['event'] = event_id
    form = PrinterLayoutForm(user=request.user, event=event_id, initial=initial)
    if action_type == 'update':
        layout_id = request.GET.get('layout_id')
        action_url = reverse('printers:printlayout_update', args=[layout_id]) if layout_id else ''
    else:
        action_url = reverse('printers:printlayout_create')
    return render(
        request,
        "printers/printers.html#printlayout_form",
        {"form": form, "action": action_url, "actions": action_type}
    )
