from django.core.management.base import BaseCommand
import os
import sys
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Avvia il runserver con DJANGO_ENV impostato su test.'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', default='127.0.0.1:8000', help='Indirizzo e porta (default: 127.0.0.1:8000)')

    def handle(self, *args, **options):
        os.environ['DJANGO_ENV'] = 'test'
        self.stdout.write(self.style.SUCCESS('DJANGO_ENV impostato su test'))
        call_command('runserver', options['addrport'])
