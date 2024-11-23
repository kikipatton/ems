from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from house.models import House

class Tenant(models.Model):
    # Add status choices
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('notice', 'Notice Given'),
        ('ended', 'Ended')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')   
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    id_cardnumber = models.PositiveIntegerField('ID NUMBER', unique=True)
    nationality = models.CharField(max_length=20, blank=True)
    house = models.OneToOneField(
        House,
        related_name='current_tenant',
        on_delete=models.SET_NULL,
        null=True
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    enddate_at = models.DateTimeField(null=True, blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def end_tenancy(self):
        """Properly end a tenancy with all related updates"""
        self.enddate_at = timezone.now()
        self.status = 'ended'
        if self.house:
            self.house.status = 'vacant'
            self.house.save()
        self.save()
    
    def save(self, *args, **kwargs):
        # If tenant is marked as ended, mark all households as ended
        if self.enddate_at and self.enddate_at <= timezone.now():
            self.household_set.filter(enddate_at__isnull=True).update(
                enddate_at=self.enddate_at
            )
        super().save(*args, **kwargs)

class Household(models.Model):    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    id_cardnumber = models.PositiveIntegerField('ID NUMBER', unique=True)
    address = models.TextField(blank=True)
    nationality = models.CharField(max_length=20)
    tenant = models.ForeignKey(
        Tenant,
        related_name='household_set',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    enddate_at = models.DateTimeField(null=True, blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"