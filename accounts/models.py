from django.contrib.auth.models import AbstractUser
from django.db import models

DAISYUI_THEMES = [
    ("light", "Light"),
    ("dark", "Dark"),
    ("cupcake", "Cupcake"),
    ("bumblebee", "Bumblebee"),
    ("emerald", "Emerald"),
    ("corporate", "Corporate"),
    ("synthwave", "Synthwave"),
    ("retro", "Retro"),
    ("cyberpunk", "Cyberpunk"),
    ("valentine", "Valentine"),
    ("halloween", "Halloween"),
    ("garden", "Garden"),
    ("forest", "Forest"),
    ("aqua", "Aqua"),
    ("lofi", "Lofi"),
    ("pastel", "Pastel"),
    ("fantasy", "Fantasy"),
    ("wireframe", "Wireframe"),
    ("black", "Black"),
    ("luxury", "Luxury"),
    ("dracula", "Dracula"),
    ("cmyk", "CMYK"),
    ("autumn", "Autumn"),
    ("business", "Business"),
    ("acid", "Acid"),
    ("lemonade", "Lemonade"),
    ("night", "Night"),
    ("coffee", "Coffee"),
    ("winter", "Winter"),
]

class User(AbstractUser):
    theme = models.CharField(
        max_length=20,
        choices=DAISYUI_THEMES,
        default="light"
    )
    personal_printer = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[:2].upper()
        elif self.username:
            return self.username[:2].upper()
        return "U"
