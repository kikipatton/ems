# views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import House, Owner
from .forms import HouseForm, OwnerForm

# House Views
class HouseListView(ListView):
    model = House
    template_name = 'house/house_list.html'
    context_object_name = 'houses'
    ordering = ['hse_number']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all houses
        houses = House.objects.all()
        
        # Total houses
        context['houses_count'] = houses.count()
        
        # Houses with owners
        context['howned_count'] = houses.filter(status='owned').count()
        
        # Developer houses
        context['downed_count'] = houses.filter(status='developer').count()
        
        # Vacant houses
        context['vhouse_count'] = houses.filter(status='vacant').count()

        return context

class HouseCreateView( CreateView):
    model = House
    form_class = HouseForm
    template_name = 'house/house_form.html'
    success_url = reverse_lazy('house-list')

class HouseUpdateView(LoginRequiredMixin, UpdateView):
    model = House
    form_class = HouseForm
    success_url = reverse_lazy('house-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'House updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating house. Please check the form.')
        return super().form_invalid(form)

class HouseDeleteView(LoginRequiredMixin, DeleteView):
    model = House
    template_name = 'houses/house_confirm_delete.html'
    success_url = reverse_lazy('house-list')

# Owner Views
class OwnerListView(LoginRequiredMixin, ListView):
    model = Owner
    template_name = 'owners/owner_list.html'
    context_object_name = 'owners'
    ordering = ['-created_at']

class OwnerCreateView(LoginRequiredMixin, CreateView):
    model = Owner
    form_class = OwnerForm
    template_name = 'owners/owner_form.html'
    success_url = reverse_lazy('owner-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Owner
    form_class = OwnerForm
    template_name = 'owners/owner_form.html'
    success_url = reverse_lazy('owner-list')

class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Owner
    template_name = 'owners/owner_confirm_delete.html'
    success_url = reverse_lazy('owner-list')