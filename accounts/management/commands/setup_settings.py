from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Imposta la variabile d\'ambiente DJANGO_ENV (dev, prod, test) per la sessione corrente.'

    def add_arguments(self, parser):
        parser.add_argument('env', type=str, choices=['dev', 'prod', 'test'], help='Ambiente da impostare (dev, prod, test)')

    def handle(self, *args, **options):
        env = options['env']
        os.environ['DJANGO_ENV'] = env
        self.stdout.write(self.style.SUCCESS(f"DJANGO_ENV impostato a '{env}'. Ricorda che questa impostazione vale solo per il processo corrente."))
