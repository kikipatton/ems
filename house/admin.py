from django.contrib import admin
from .models import House, Owner

# Register your models here.
default_auto_field = 'django.db.models.BigAutoField'
admin.site.register(House)
admin.site.register(Owner)