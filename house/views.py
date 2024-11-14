# views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import House, Owner
from .forms import HouseForm, OwnerForm

# House Views
class HouseListView(LoginRequiredMixin, ListView):
    model = House
    template_name = 'houses/house_list.html'
    context_object_name = 'houses'
    ordering = ['hse_number']

class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    template_name = 'houses/house_form.html'
    success_url = reverse_lazy('house-list')

class HouseUpdateView(LoginRequiredMixin, UpdateView):
    model = House
    form_class = HouseForm
    template_name = 'houses/house_form.html'
    success_url = reverse_lazy('house-list')

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