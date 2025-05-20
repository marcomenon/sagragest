from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Event(models.Model):
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

    name = models.CharField(max_length=100)
    year = models.IntegerField()
    active = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="events")
    option_client = models.BooleanField(default=False, verbose_name="Richiede cliente")
    option_table = models.BooleanField(default=False, verbose_name="Richiede tavolo")
    option_cover = models.BooleanField(default=False, verbose_name="Richiede coperto")
    pay_cover = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    pay_takeaway = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    def save(self, *args, **kwargs):
        if self.active:
            # Disattiva altri eventi dello stesso gruppo
            Event.objects.filter(group=self.group, active=True).exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} ({self.year})"


class CategoryTemplate(models.Model):
    class Meta:
        verbose_name = "CategoryTemplate"
        verbose_name_plural = "CategoryTemplates"

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ProductTemplate(models.Model):
    class Meta:
        verbose_name = "ProductTemplate"
        verbose_name_plural = "ProductTemplates"

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CategoryEvent(models.Model):
    class Meta:
        verbose_name = "CategoryEvent"
        verbose_name_plural = "CategoryEvents"
        ordering = ["display_order"]  # Ordina automaticamente per display_order

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="category_events")
    category = models.ForeignKey(CategoryTemplate, on_delete=models.CASCADE, related_name="event_links")
    display_order = models.PositiveIntegerField(null=True, blank=True)
    display_elements = models.PositiveIntegerField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.display_order is None:
            max_order = CategoryEvent.objects.filter(event=self.event).aggregate(models.Max("display_order"))["display_order__max"] or 0
            self.display_order = max_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} ({self.event.name})"


class ProductEvent(models.Model):
    class Meta:
        verbose_name = "ProductEvent"
        verbose_name_plural = "ProductEvents"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="product_events")
    product = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name="event_links")
    category = models.ForeignKey(CategoryEvent, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    display_order = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.display_order is None:
            max_order = ProductEvent.objects.filter(category=self.category).aggregate(models.Max("display_order"))[
                "display_order__max"
            ] or 0
            self.display_order = max_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.event.name})"


class Daytime(models.Model):
    class Meta:
        verbose_name = "Daytime"
        verbose_name_plural = "Daytimes"
        ordering = ["-start"]

    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="daytimes")
    note = models.TextField(blank=True)

    def is_open(self):
        return self.end is None

    def __str__(self):
        return f"Giornata per {self.event.name} del {self.start.strftime('%d/%m/%Y')}"

class OrderStatus(models.TextChoices):
    ORDERED = "ORDERED", _("Ordinato")
    IN_PREPARATION = "IN_PREPARATION", _("In preparazione")
    READY = "READY", _("Pronto")
    CANCELLED = "CANCELLED", _("Annullato")


class Order(models.Model):
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    number = models.PositiveIntegerField()
    daytime = models.ForeignKey(Daytime, on_delete=models.CASCADE, related_name="orders")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.ORDERED)
    notes = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    table_number = models.PositiveIntegerField(default=0)
    cover = models.PositiveIntegerField(default=1)
    is_takeaway = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Creato da")
    client = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cliente")
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) 
    
    def __str__(self):
        return f"Ordine #{self.number}"
    
    @classmethod
    def get_next_number_for_daytime(cls, daytime):
        """Restituisce il prossimo numero ordine disponibile per una giornata."""
        last_order = cls.objects.filter(daytime=daytime).order_by("-number").first()
        if last_order:
            return last_order.number + 1
        return 1

class OrderItem(models.Model):
    class Meta:
        verbose_name = "OrderItem"
        verbose_name_plural = "OrderItems"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_event = models.ForeignKey(ProductEvent, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    note = models.TextField(blank=True)
    price_at_order_time = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_price = self.price_at_order_time * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product_event.product.name}"