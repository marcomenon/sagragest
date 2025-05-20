from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
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
    help = 'Crea un superuser leggendo da .env se presente, altrimenti in modo interattivo.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = get_env_or_input("DJANGO_SUPERUSER_USERNAME", "Username superuser: ")
        password = get_env_or_input("DJANGO_SUPERUSER_PASSWORD", "Password superuser: ")
        email = get_env_or_input("DJANGO_SUPERUSER_EMAIL", "Email superuser: ")
        first_name = get_env_or_input("DJANGO_SUPERUSER_NAME", "Nome: ")
        last_name = get_env_or_input("DJANGO_SUPERUSER_LAST_NAME", "Cognome: ")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(self.style.SUCCESS("Superuser creato."))
        else:
            self.stdout.write(self.style.WARNING("Superuser già esistente."))
