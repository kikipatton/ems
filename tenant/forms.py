from django import forms
from .models import Tenant, Household, Tenancy
from house.models import House
from django.db import models 


class TenantForm(forms.ModelForm):
    house = forms.ModelChoiceField(
        queryset=House.objects.filter(
            # A house is available if it has no active tenancy
            ~models.Exists(
                Tenancy.objects.filter(
                    house=models.OuterRef('pk'),
                    end_date__isnull=True
                )
            )
        ),
        required=False,
        label='House (Optional)'
    )

    class Meta:
        model = Tenant
        fields = [
            'first_name', 'middle_name', 'last_name',
            'email', 'phone_number', 'id_cardnumber',
            'nationality'
        ]

    def save(self, commit=True, created_by=None):
        tenant = super().save(commit=False)
        if created_by:
            tenant.created_by = created_by
        
        if commit:
            tenant.save()
            
            # If house is selected, create a tenancy
            house = self.cleaned_data.get('house')
            if house:
                Tenancy.objects.create(
                    tenant=tenant,
                    house=house,
                    created_by=created_by
                )
                # Update house status
                house.status = 'occupied'
                house.save()
        
        return tenant

    def clean(self):
        cleaned_data = super().clean()
        house = cleaned_data.get('house')
        
        if house:
            # Check if house is already occupied
            existing_tenancy = Tenancy.objects.filter(
                house=house,
                end_date__isnull=True
            ).exists()
            
            if existing_tenancy:
                raise forms.ValidationError({
                    'house': 'This house is already occupied.'
                })
        
        return cleaned_data

class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = [
            'first_name', 'last_name', 'email',
            'phone_number', 'id_cardnumber',
            'nationality', 'address'
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation if needed
        return cleaned_data

class TenancyForm(forms.ModelForm):
    class Meta:
        model = Tenancy
        fields = ['house']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['house'].queryset = House.objects.filter(
            ~models.Exists(
                Tenancy.objects.filter(
                    house=models.OuterRef('pk'),
                    end_date__isnull=True
                )
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        house = cleaned_data.get('house')
        
        if house:
            existing_tenancy = Tenancy.objects.filter(
                house=house,
                end_date__isnull=True
            ).exists()
            
            if existing_tenancy:
                raise forms.ValidationError({
                    'house': 'This house is already occupied.'
                })
        
        return cleaned_data