from django.db import models
from django.contrib.auth.models import User
from house.models import House 

class Meter(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('damaged', 'Damaged'),
        ('replaced', 'Replaced')
    ]

    meter_number = models.CharField(max_length=50, unique=True)
    house = models.ForeignKey(House, on_delete=models.PROTECT, related_name='meters')
    installation_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.meter_number} - {self.house}"

    def deactivate(self):
        self.status = 'inactive'
        self.is_current = False
        self.save()

class MeterReading(models.Model):
    meter = models.ForeignKey(Meter, on_delete=models.PROTECT, related_name='readings')
    current_reading = models.DecimalField(max_digits=10, decimal_places=2)
    previous_reading = models.DecimalField(max_digits=10, decimal_places=2)
    reading_date = models.DateField()
    read_by = models.ForeignKey(User, on_delete=models.PROTECT)
    consumption = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rate_per_unit = models.DecimalField(max_digits=6, decimal_places=2, default=171)

    @property
    def bill_amount(self):
       return round(self.consumption * self.rate_per_unit, 2)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new readings
            last_reading = self.meter.readings.order_by('-reading_date', '-id').first()
            self.previous_reading = last_reading.current_reading if last_reading else 0
        
        self.consumption = self.current_reading - self.previous_reading
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-reading_date', '-id']