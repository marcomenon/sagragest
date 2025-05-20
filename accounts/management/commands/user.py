from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Crea un utente normale (non staff, non superuser) in modo interattivo.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = input("Username: ")
        password = input("Password: ")
        email = input("Email: ")
        first_name = input("Nome: ")
        last_name = input("Cognome: ")
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            self.stdout.write(self.style.SUCCESS("Utente normale creato."))
        else:
            self.stdout.write(self.style.WARNING("Utente già esistente."))
