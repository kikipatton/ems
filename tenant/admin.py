from django.contrib import admin
from .models import Tenant, Household

# Register your models here.
admin.site.register(Tenant)
admin.site.register(Household)