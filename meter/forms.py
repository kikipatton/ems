from django import forms
from django.core.exceptions import ValidationError
from .models import Meter, MeterReading

class MeterForm(forms.ModelForm):
    class Meta:
        model = Meter
        fields = ['meter_number', 'installation_date']

    def clean_meter_number(self):
        meter_number = self.cleaned_data.get('meter_number')
        if Meter.objects.filter(meter_number=meter_number, is_current=True).exists():
            raise forms.ValidationError("This meter number is already in use")
        return meter_number

class MeterReplacementForm(forms.ModelForm):
    new_meter_number = forms.CharField(max_length=50)
    
    class Meta:
        model = Meter
        fields = ['status']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('status') not in ['inactive', 'damaged']:
            raise forms.ValidationError("Meter must be inactive or damaged to be replaced")
        return cleaned_data

class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ['current_reading']

    def __init__(self, meter=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meter = meter
        if self.meter:
            last_reading = self.meter.readings.order_by('-reading_date', '-id').first()
            self.last_reading_value = last_reading.current_reading if last_reading else 0
            self.fields['previous_reading'] = forms.DecimalField(
                initial=self.last_reading_value,
                disabled=True,
                required=False
            )

    def clean(self):
        cleaned_data = super().clean()
        current_reading = cleaned_data.get('current_reading')
        
        if current_reading and self.meter:
            last_reading = self.meter.readings.order_by('-reading_date', '-id').first()
            last_reading_value = last_reading.current_reading if last_reading else 0
            
            if current_reading <= last_reading_value:
                raise ValidationError({
                    'current_reading': f'Current reading must be greater than the previous reading ({last_reading_value})'
                })
        
        return cleaned_data