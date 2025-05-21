from django.shortcuts import render, get_object_or_404
from core.utils import admin_required
from django.contrib.auth.models import Group
from sagragest.models import Order, Event, Daytime, CategoryEvent, ProductEvent, OrderItem, OrderStatus
from django.db.models import Sum
from reports.filters import ReportFilter
from collections import defaultdict
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML

@admin_required
def reports_dashboard(request):
    
    f = ReportFilter(request.GET, queryset=Order.objects.all(), user=request.user)

    orders = f.qs
    total_orders = orders.count()
    total_income = orders.aggregate(Sum('total'))['total__sum'] or 0

    events_count = orders.values('event').distinct().count()
    daytimes_count = orders.values('daytime').distinct().count()

    mode = request.GET.get('mode', 'qty')

    selected_event = None
    selected_daytime = None
    if f.form.is_valid():
        selected_event = f.form.cleaned_data.get('event')
        selected_daytime = f.form.cleaned_data.get('daytime')

    categories_data = defaultdict(list)
    if selected_event:
        if selected_daytime:
            daytimes_list = [selected_daytime]
        else:
            # Prendi gli ID delle giornate dagli ordini filtrati
            daytimes_ids = orders.filter(daytime__isnull=False).values_list('daytime_id', flat=True).distinct()
            daytimes_list = list(
                Daytime.objects.filter(
                    event=selected_event,
                    id__in=daytimes_ids
                ).order_by('start')
            )
        category_totals = defaultdict(lambda: [0] * (len(daytimes_list)))
        col_totals = [0 for _ in daytimes_list]
        grand_total = 0

        categories = CategoryEvent.objects.filter(event=selected_event).order_by('display_order')
        for category in categories:
            products = ProductEvent.objects.filter(category=category).order_by('display_order')
            for product in products:
                row = {
                    'product': product.product.name,
                    'values': [],
                    'row_total': 0
                }
                for idx, dt in enumerate(daytimes_list):
                    items = OrderItem.objects.filter(order__daytime=dt, product_event=product, order__in=orders)
                    value = items.aggregate(
                        total=Sum('total_price') if mode == 'income' else Sum('quantity')
                    )['total'] or 0

                    row['values'].append(value)
                    row['row_total'] += value
                    col_totals[idx] += value
                    category_totals[category.category.name][idx] += value

                grand_total += row['row_total']
                categories_data[category.category.name].append(row)
    else:
        daytimes_list = []
        category_totals = {}
        col_totals = []
        grand_total = 0

    context = {
        'filter': f,
        'orders_count': total_orders,
        'income': total_income,
        'events_count': events_count,
        'daytimes_count': daytimes_count,
        'categories_data': dict(categories_data),
        'category_totals': dict(category_totals),
        'daytimes_list': daytimes_list,
        'col_totals': col_totals,
        'grand_total': grand_total,
        'mode': mode,
        'is_superuser': request.user.is_superuser,
        'selected_event': selected_event,
    }

    if request.htmx:
        return render(request, "reports/reports.html#filters-and-dashboard", context)

    return render(request, "reports/reports.html", context)

@admin_required
def reports_monitor(request, daytime_id):
    daytime = get_object_or_404(Daytime, id=daytime_id)
    # Ordini READY (max 8, ultimi)
    ready_orders = list(Order.objects.filter(daytime=daytime, status=OrderStatus.READY).order_by('-created_at')[:8])
    # Ordini IN_PREPARATION (max 8, ultimi)
    inprep_orders = list(Order.objects.filter(daytime=daytime, status=OrderStatus.IN_PREPARATION).order_by('-created_at')[:8])
    context = {
        'daytime': daytime,
        'ready_orders': ready_orders,
        'inprep_orders': inprep_orders,
    }
    if request.htmx:
        # Se la richiesta è HTMX aggiorna solo il blocco della tabella ordini
        return render(request, "reports/monitor.html#orders-monitor", context)
    return render(request, "reports/monitor.html", context)

@admin_required
def reports_print(request):
    f = ReportFilter(request.GET, queryset=Order.objects.all(), user=request.user)
    orders = f.qs
    total_orders = orders.count()
    total_income = orders.aggregate(Sum('total'))['total__sum'] or 0

    events_count = orders.values('event').distinct().count()
    daytimes_count = orders.values('daytime').distinct().count()

    mode = request.GET.get('mode', 'qty')

    selected_event = None
    selected_daytime = None
    if f.form.is_valid():
        selected_event = f.form.cleaned_data.get('event')
        selected_daytime = f.form.cleaned_data.get('daytime')

    categories_data = defaultdict(list)
    if selected_event:
        if selected_daytime:
            daytimes_list = [selected_daytime]
        else:
            daytimes_ids = orders.filter(daytime__isnull=False).values_list('daytime_id', flat=True).distinct()
            daytimes_list = list(
                Daytime.objects.filter(
                    event=selected_event,
                    id__in=daytimes_ids
                ).order_by('start')
            )
        category_totals = defaultdict(lambda: [0] * (len(daytimes_list)))
        col_totals = [0 for _ in daytimes_list]
        grand_total = 0

        categories = CategoryEvent.objects.filter(event=selected_event).order_by('display_order')
        for category in categories:
            products = ProductEvent.objects.filter(category=category).order_by('display_order')
            for product in products:
                row = {
                    'product': product.product.name,
                    'values': [],
                    'row_total': 0
                }
                for idx, dt in enumerate(daytimes_list):
                    items = OrderItem.objects.filter(order__daytime=dt, product_event=product, order__in=orders)
                    value = items.aggregate(
                        total=Sum('total_price') if mode == 'income' else Sum('quantity')
                    )['total'] or 0

                    row['values'].append(value)
                    row['row_total'] += value
                    col_totals[idx] += value
                    category_totals[category.category.name][idx] += value

                grand_total += row['row_total']
                categories_data[category.category.name].append(row)
    else:
        daytimes_list = []
        category_totals = {}
        col_totals = []
        grand_total = 0

    context = {
        'filter': f,
        'orders_count': total_orders,
        'income': total_income,
        'events_count': events_count,
        'daytimes_count': daytimes_count,
        'categories_data': dict(categories_data),
        'category_totals': dict(category_totals),
        'daytimes_list': daytimes_list,
        'col_totals': col_totals,
        'grand_total': grand_total,
        'mode': mode,
        'is_superuser': request.user.is_superuser,
        'selected_event': selected_event,
    }

    html_string = render_to_string("reports/print_reports.html", context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="report.pdf"'
    return response