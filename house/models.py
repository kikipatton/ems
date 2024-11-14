from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class House(models.Model):
    UNIT_CHOICES = [
        ('2BR', '2Bedroom'),
        ('3BR', '3Bedroom'),
    ]
    
    hse_number = models.CharField('House Number', max_length=50, unique=True)
    unit_type = models.CharField(
        max_length=10, 
        choices=UNIT_CHOICES, 
        verbose_name='Unit Type'
    )
    handover = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        owner = self.owner_set.first()  # Get the first owner if exists
        return f"House {self.hse_number} - {owner.get_full_name() if owner else 'Vacant'}"

    class Meta:
        ordering = ['hse_number']
        verbose_name = 'House'
        verbose_name_plural = 'Houses'

class Owner(models.Model):    
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    kra_pin = models.CharField('KRA PIN', max_length=20)
    address = models.TextField()
    nationality = models.CharField(max_length=20)
    house = models.ForeignKey(
        House, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='owner_set'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.get_full_name()} - House: {self.house.hse_number if self.house else 'No House'}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Owner'
        verbose_name_plural = 'Owners'