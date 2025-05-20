import os
import cups
import tempfile
from django.template.loader import render_to_string
from printers.models import PrinterLayout
from weasyprint import HTML
from core.settings.common.paths import PRINTERS_DIR
from django.conf import settings

def get_cups_connection():
    """Restituisce una connessione CUPS usando host e porta dalle impostazioni."""
    host = getattr(settings, "CUPS_HOST", "localhost")
    port = getattr(settings, "CUPS_PORT", "631")
    return cups.Connection(host=host, port=int(port))

def get_cups_printers():
    """Restituisce la lista dei nomi delle stampanti CUPS disponibili."""
    conn = get_cups_connection()
    return list(conn.getPrinters().keys())

def print_for_user(order):
    """
    Stampa l'ordine sulla stampante personale dell'utente tramite layout utente e PDF.
    """
    user = getattr(order, 'created_by', None)
    if not user or not getattr(user, 'personal_printer', None):
        print(f"[COMMAND] Nessuna stampante personale configurata per l'utente dell'ordine #{order.number}")
        return
    printer_name = user.personal_printer
    layout = PrinterLayout.objects.filter(event=order.event, is_user=True).first()
    if not layout:
        print(f"[COMMAND] Nessun layout utente trovato per l'evento dell'ordine #{order.number}")
        return
    html = render_to_string(layout.layout_path, {"order": order, "items": order.items.all(), "layout": layout.name})
    # Ricava la directory del layout per usarla come base_url
    layout_dir = os.path.dirname(os.path.join(PRINTERS_DIR, 'templates', layout.layout_path))
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html, base_url=layout_dir).write_pdf(tmp.name)
        tmp_path = tmp.name
    conn = get_cups_connection()
    try:
        job_id = conn.printFile(printer_name, tmp_path, f"Ordine #{order.number}", {})
        print(f"[COMMAND] Stampa inviata alla stampante personale '{printer_name}' per Ordine #{order.number} (job id: {job_id})")
    except cups.IPPError as e:
        print(f"[COMMAND] Errore durante la stampa su '{printer_name}': {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def print_for_category(order):
    """
    Stampa l'ordine su tutte le stampanti di categoria dell'evento, filtrando gli items per categoria del layout.
    """
    from django.conf import settings
    layouts = PrinterLayout.objects.filter(event=order.event, is_user=False)
    for layout in layouts:
        if not layout.printer:
            continue
        categories = layout.category.all()
        items = order.items.filter(product_event__category__in=categories)
        if not items.exists():
            continue
        html = render_to_string(layout.layout_path, {"order": order, "items": items, "layout": layout.name})
        layout_dir = os.path.dirname(os.path.join(PRINTERS_DIR, 'templates', layout.layout_path))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            HTML(string=html, base_url=layout_dir).write_pdf(tmp.name)
            tmp_path = tmp.name
        conn = get_cups_connection()
        try:
            job_id = conn.printFile(layout.printer, tmp_path, f"Ordine #{order.number} - {layout.name}", {})
            print(f"[COMMAND] Stampa inviata alla stampante '{layout.printer}' per Ordine #{order.number} (job id: {job_id})")
        except cups.IPPError as e:
            print(f"[COMMAND] Errore durante la stampa su '{layout.printer}': {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

def print_for_delete(order):
    """
    Invia una stampa di notifica cancellazione per ogni layout (utente e di categoria) dell'evento,
    anche se la stampante è la stessa.
    """
    from django.conf import settings
    template_path = "printers/delete_template_layout.html"
    layouts = PrinterLayout.objects.filter(event=order.event)
    # Stampa per ogni layout
    for layout in layouts:
        if not layout.printer:
            continue
        html = render_to_string(template_path, {"order": order})
        layout_dir = os.path.dirname(os.path.join(PRINTERS_DIR, 'templates', template_path))
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            HTML(string=html, base_url=layout_dir).write_pdf(tmp.name)
            tmp_path = tmp.name
        conn = get_cups_connection()
        try:
            job_id = conn.printFile(layout.printer, tmp_path, f"Ordine #{order.number} ANNULLATO - {layout.name}", {})
            print(f"[COMMAND] Notifica cancellazione inviata a '{layout.printer}' per Ordine #{order.number} (layout: {layout.name}, job id: {job_id})")
        except cups.IPPError as e:
            print(f"[COMMAND] Errore durante la stampa su '{layout.printer}' (layout: {layout.name}): {e}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    # Stampa anche sulla stampante personale dell'utente se esiste e non già inclusa nei layout
    user = getattr(order, 'created_by', None)
    if user and getattr(user, 'personal_printer', None):
        user_printer = user.personal_printer
        # Verifica se già usata in un layout utente
        if not layouts.filter(printer=user_printer, is_user=True).exists():
            html = render_to_string(template_path, {"order": order})
            layout_dir = os.path.dirname(os.path.join(PRINTERS_DIR, 'templates', template_path))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                HTML(string=html, base_url=layout_dir).write_pdf(tmp.name)
                tmp_path = tmp.name
            conn = get_cups_connection()
            try:
                job_id = conn.printFile(user_printer, tmp_path, f"Ordine #{order.number} ANNULLATO - personale", {})
                print(f"[COMMAND] Notifica cancellazione inviata a stampante personale '{user_printer}' per Ordine #{order.number} (job id: {job_id})")
            except cups.IPPError as e:
                print(f"[COMMAND] Errore durante la stampa su stampante personale '{user_printer}': {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

def print_action(order, action):
    """
    Gestisce la stampa su CUPS in base all'azione richiesta per l'ordine.
    """
    if action == "PRINT_FOR_USER":
        print_for_user(order)
    elif action == "PRINT_FOR_CATEGORIES":
        print_for_category(order)
    elif action == "PRINT_FOR_ALL":
        if order.status == "ORDERED":  # Sostituisci con OrderStatus.ORDERED se disponibile
            print_for_user(order)
            print_for_category(order)
        elif order.status == "CANCELLED":  # Sostituisci con OrderStatus.CANCELLED se disponibile
            print_for_delete(order)
    else:
        print(f"[COMMAND] Azione '{action}' non riconosciuta per Ordine #{order.number}")
    return
