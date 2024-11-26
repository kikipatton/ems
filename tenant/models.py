from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from house.models import House

class Tenant(models.Model):
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
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_current_tenancy(self):
        """Get the current active tenancy for this tenant"""
        return self.tenancy_set.filter(
            end_date__isnull=True
        ).first()
    
    def get_current_house(self):
        """Get the current house for this tenant"""
        current_tenancy = self.get_current_tenancy()
        return current_tenancy.house if current_tenancy else None

class Tenancy(models.Model):
    """Model to track tenant occupation of houses over time"""
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='tenancy_set'
    )
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='tenancy_set'
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Tenancies"
        
    def __str__(self):
        return f"{self.tenant.get_full_name()} - {self.house}"
        
    def end_tenancy(self):
        """Properly end a tenancy with all related updates"""
        self.end_date = timezone.now()
        self.tenant.status = 'ended'
        self.house.status = 'vacant'
        
        # End all related household memberships
        for household in self.household_set.all():
            household.enddate_at = timezone.now()
            household.save()
            
        self.tenant.save()
        self.house.save()
        self.save()

class Household(models.Model):    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    id_cardnumber = models.PositiveIntegerField('ID NUMBER', unique=True)
    address = models.TextField(blank=True)
    nationality = models.CharField(max_length=20)
    tenancy = models.ForeignKey(
        Tenancy,
        on_delete=models.CASCADE,
        related_name='household_set',
        null=True  # This is important for the migration
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    enddate_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"