from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from house.models import House
from .models import Meter, MeterReading
from django.utils.timezone import now
from .forms import MeterForm, MeterReplacementForm, MeterReadingForm

class HouseMeterView(LoginRequiredMixin, DetailView):
    model = House
    template_name = 'meter/house_meter.html'
    context_object_name = 'house'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meter = self.object.meters.filter(is_current=True).first()
        context['meter'] = meter
        
        if not meter:
            return context
            
        readings = meter.readings.all()
        context['readings'] = readings
        
        if meter.readings.exists():
            context['previous_reading'] = meter.readings.order_by('-reading_date', '-id').first().current_reading
        else:
            context['previous_reading'] = 0
            return context
            
        total_consumption = sum(reading.consumption for reading in readings)
        total_bill = sum(reading.bill_amount for reading in readings)
        highest_reading = max(readings, key=lambda x: x.consumption)
        
        context.update({
            'total_consumption': total_consumption,
            'total_bill': total_bill,
            'highest_reading': highest_reading,
            'avg_consumption': round(total_consumption / readings.count(), 2)
        })
        
        return context

class MeterCreateView(LoginRequiredMixin, CreateView):
    model = Meter
    template_name = 'meter/house_meter.html'
    form_class = MeterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        house = get_object_or_404(House, pk=self.kwargs['house_pk'])
        context['house'] = house
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        house = get_object_or_404(House, pk=self.kwargs['house_pk'])
        
        if form.is_valid():
            meter = form.save(commit=False)
            meter.house = house
            
            if house.meters.filter(is_current=True).exists():
                messages.error(request, 'This house already has an active meter')
            else:
                meter.save()
                messages.success(request, 'Meter added successfully')
                return self.form_valid(form)
                
        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('house-meter', kwargs={'pk': self.kwargs['house_pk']})

class MeterReplaceView(LoginRequiredMixin, UpdateView):
   model = Meter
   template_name = 'meter/meter_replace.html'
   form_class = MeterReplacementForm
   
   def form_valid(self, form):
       old_meter = form.save(commit=False)
       old_meter.is_current = False
       old_meter.save()
       
       Meter.objects.create(
           meter_number=form.cleaned_data['new_meter_number'],
           house=old_meter.house,
           installation_date=now().date(),
           is_current=True
       )
       messages.success(self.request, 'Meter replaced successfully')
       return super().form_valid(form)

   def get_success_url(self):
       return reverse_lazy('house-meter', kwargs={'pk': self.object.house.pk})

class ReadingCreateView(LoginRequiredMixin, CreateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'meter/house_meter.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['meter'] = get_object_or_404(Meter, pk=self.kwargs['meter_pk'])
        return kwargs

    def form_valid(self, form):
        form.instance.meter_id = self.kwargs['meter_pk']
        form.instance.read_by = self.request.user
        form.instance.reading_date = timezone.now().date()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('house-meter', kwargs={'pk': self.object.meter.house.pk})