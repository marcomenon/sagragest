from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from dotenv import load_dotenv
import os
from core.settings.common.paths import BASE_DIR

load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_env_or_input(var, prompt):
    value = os.getenv(var)
    if not value:
        value = input(prompt)
    return value

class Command(BaseCommand):
    help = 'Aggiorna Site.name e Site.domain leggendo da .env se presente, altrimenti in modo interattivo.'

    def handle(self, *args, **options):
        site_name = get_env_or_input("SITE_NAME", "Nome sito: ")
        site_domain = get_env_or_input("SITE_DOMAIN", "Dominio sito: ")
        site = Site.objects.get_current()
        site.name = site_name
        site.domain = site_domain
        site.save()
        self.stdout.write(self.style.SUCCESS("Site aggiornato."))
