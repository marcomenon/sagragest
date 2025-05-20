from django import template
register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def replace(value, arg):
    """Sostituisce tutte le occorrenze di una sottostringa con un'altra. Usa: |replace:",." """
    try:
        old, new = arg.split(',')
        return str(value).replace(old, new)
    except Exception:
        return value

@register.filter
def dict_get(d, key):
    return d.get(key, [])

@register.filter
def dict_get_alt(d, key):
    """Versione alternativa di dict_get: restituisce d.get(key, '') invece di d.get(key, [])"""
    return d.get(key, '')

@register.filter
def index(sequence, position):
    try:
        return sequence[int(position)]
    except (IndexError, ValueError, TypeError):
        return 0

@register.filter
def get_range(value):
    return range(value)

@register.filter
def sum_list(value):
    try:
        return sum(value)
    except Exception:
        return 0

@register.filter
def product_name(products_map, pid):
    """Restituisce il nome del prodotto dato il products_map e l'id, oppure l'id se non trovato."""
    try:
        return products_map.get(pid) or pid
    except Exception:
        return pid

@register.filter
def pluck(sequence, attr):
    """Estrae una lista di valori anche da dizionari annidati (es: 'product_event_id')."""
    result = []
    for item in sequence:
        value = item
        # Gestione dizionario o oggetto
        if isinstance(value, dict):
            value = value.get(attr, None)
        else:
            value = getattr(value, attr, None)
        if value is not None:
            result.append(str(value))
        else:
            result.append(None)
    return result

