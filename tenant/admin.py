from django.contrib import admin
from .models import Tenant, Household, Tenancy

# Register your models here.
admin.site.register(Tenant)
admin.site.register(Tenancy)
admin.site.register(Household)