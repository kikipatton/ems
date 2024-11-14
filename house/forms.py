from django import forms
from .models import House, Owner

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['hse_number', 'unit_type', 'status', 'handover']

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = [
            'first_name', 
            'middle_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'kra_pin', 
            'address', 
            'nationality',
            'house'  
        ]