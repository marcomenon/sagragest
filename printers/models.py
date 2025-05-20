import os
import shutil
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from sagragest.models import Event, CategoryEvent

class PrinterLayout(models.Model):
    name = models.CharField(max_length=100)
    printer = models.CharField(max_length=100, null=True, blank=True)
    layout_path = models.CharField(max_length=255)
    is_user = models.BooleanField(default=False)
    category = models.ManyToManyField('sagragest.CategoryEvent', blank=True, related_name='layouts')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (('name', 'event'),)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        creating = self._state.adding
        if not creating and self.pk:
            old = PrinterLayout.objects.get(pk=self.pk)
            if not self.layout_path:
                self.layout_path = old.layout_path
        super().save(*args, **kwargs)
        if creating and self.event:
            safe_event_name = str(self.event.name).replace(' ', '_')
            layout_dir = os.path.join(
                settings.PRINTERS_DIR, 'templates', 'printers', 'layout',
                str(self.event.year), safe_event_name
            )
            os.makedirs(layout_dir, exist_ok=True)
            # Scegli il template layout in base a is_user
            if self.is_user:
                layout_template = os.path.join(settings.PRINTERS_DIR, 'templates', 'printers', 'user_template_layout.html')
            else:
                layout_template = os.path.join(settings.PRINTERS_DIR, 'templates', 'printers', 'category_template_layout.html')
            # Banner unico
            banner_template = os.path.join(settings.PRINTERS_DIR, 'templates', 'printers', 'template_banner.png')
            dest_layout = os.path.join(layout_dir, f'{self.name}.html')
            dest_banner = os.path.join(layout_dir, 'template_banner.png')
            if not os.path.exists(dest_layout):
                shutil.copyfile(layout_template, dest_layout)
            if os.path.exists(banner_template) and not os.path.exists(dest_banner):
                shutil.copyfile(banner_template, dest_banner)
            rel_path = os.path.relpath(dest_layout, os.path.join(settings.PRINTERS_DIR, 'templates'))
            if self.layout_path != rel_path:
                self.layout_path = rel_path
                super().save(update_fields=['layout_path'])

    def delete(self, *args, **kwargs):
        if self.event:
            safe_event_name = str(self.event.name).replace(' ', '_')
            layout_dir = os.path.join(
                settings.PRINTERS_DIR, 'templates', 'printers', 'layout',
                str(self.event.year), safe_event_name
            )
            file_path = os.path.join(layout_dir, f'{self.name}.html')
            banner_path = os.path.join(layout_dir, 'template_banner.png')
            template_path_user = os.path.join(settings.PRINTERS_DIR, 'templates', 'printers', 'user_template_layout.html')
            template_path_category = os.path.join(settings.PRINTERS_DIR, 'templates', 'printers', 'category_template_layout.html')
            if os.path.exists(file_path) and os.path.abspath(file_path) not in [os.path.abspath(template_path_user), os.path.abspath(template_path_category)]:
                os.remove(file_path)
            if os.path.exists(banner_path):
                os.remove(banner_path)
        super().delete(*args, **kwargs)