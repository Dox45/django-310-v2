from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class Space(models.Model):
    CATEGORY_CHOICES = [
        ('Workspace', 'Workspace'),
        ('Meeting room', 'Meeting room'),
        ('Conference', 'Conference'),
    ]
    PRICE_UNIT_CHOICES = [
        ('hour', 'hour'),
        ('day', 'day'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    price_unit = models.CharField(max_length=10, choices=PRICE_UNIT_CHOICES)
    min_duration = models.IntegerField(default=1, help_text="Minimum booking duration in units (hours or days)")
    max_duration = models.IntegerField(default=24, help_text="Maximum booking duration in units (hours or days)")
    capacity = models.IntegerField(help_text="Maximum capacity of the space")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category}) - ₦{self.price_per_unit:,.2f}/{self.price_unit}"


class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours or days")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', '-start_time']

    def clean(self):
        # Base validation to prevent logical bugs
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        
        # Ensure duration meets space requirements
        if self.duration:
            if self.duration < self.space.min_duration:
                raise ValidationError(f"Duration must be at least {self.space.min_duration} {self.space.price_unit}(s).")
            if self.duration > self.space.max_duration:
                raise ValidationError(f"Duration cannot exceed {self.space.max_duration} {self.space.price_unit}(s).")

    def save(self, *args, **kwargs):
        # Auto-compute total price if not provided
        if not self.total_price:
            self.total_price = self.duration * self.space.price_per_unit
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        time_str = f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
        return f"{self.customer.name} - {self.space.name} on {self.booking_date} ({time_str})"


class BlockedDate(models.Model):
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='blocked_dates', null=True, blank=True, help_text="If empty, blocks all spaces")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True, help_text="If empty, blocks the entire day")
    end_time = models.TimeField(null=True, blank=True, help_text="If empty, blocks the entire day")
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        space_name = self.space.name if self.space else "All Spaces"
        time_str = "Full Day"
        if self.start_time and self.end_time:
            time_str = f"{self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"
        return f"{space_name} blocked on {self.date} ({time_str}) - Reason: {self.reason or 'None'}"

