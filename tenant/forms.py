# forms.py
from django import forms
from .models import Tenant, Household
from house.models import House
from django.db import models

class TenantForm(forms.ModelForm):
    house = forms.ModelChoiceField(
        queryset=House.objects.filter(current_tenant__isnull=True),
        empty_label="Select a house",
        label="House Number"
    )
    
    class Meta:
        model = Tenant
        fields = [
            'first_name', 'middle_name', 'last_name', 'email', 
            'phone_number', 'id_cardnumber', 'nationality', 'house',
            'status', 'enddate_at'  # Added status field
        ]
        widgets = {
            'enddate_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'status': forms.Select(
                attrs={'class': 'form-select'}
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # Include current house in choices if editing
            self.fields['house'].queryset = House.objects.filter(
                models.Q(current_tenant__isnull=True) | 
                models.Q(pk=instance.house_id)
            )
        
        # Add Bootstrap classes and customize status field
        self.fields['status'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'handleStatusChange(this)'  # For potential JS interactions
        })
        
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        enddate_at = cleaned_data.get('enddate_at')
        
        # If status is 'ended', require end date
        if status == 'ended' and not enddate_at:
            raise forms.ValidationError(
                "End date is required when status is set to 'Ended'"
            )
            
        return cleaned_data

class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'id_cardnumber', 'address', 'nationality'
        ]