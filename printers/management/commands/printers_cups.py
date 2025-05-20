from django.core.management.base import BaseCommand
import cups

class Command(BaseCommand):
    help = 'Gestione stampanti tramite CUPS (es: list, add, remove)'  # Puoi estendere le azioni

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, choices=['list'], help='Azione da eseguire sulle stampanti (es: list)')
        # Puoi aggiungere altri argomenti per add/remove

    def handle(self, *args, **options):
        action = options['action']
        conn = cups.Connection()
        if action == 'list':
            printers = conn.getPrinters()
            if not printers:
                self.stdout.write(self.style.WARNING('Nessuna stampante trovata.'))
            for name, info in printers.items():
                self.stdout.write(f"{name}: {info['device-uri']}")
        # Qui puoi aggiungere altre azioni (add/remove)
