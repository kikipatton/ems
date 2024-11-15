from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import House, Owner
from .forms import HouseForm, OwnerForm

class HouseListView(LoginRequiredMixin, ListView):
    model = House
    template_name = 'house/house_list.html'
    context_object_name = 'houses'
    ordering = ['hse_number']
    paginate_by = 100
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        
        if search_query:
            queryset = queryset.filter(
                Q(hse_number__icontains=search_query) |
                Q(owner_set__first_name__icontains=search_query) |
                Q(owner_set__last_name__icontains=search_query) |
                Q(owner_set__email__icontains=search_query) |
                Q(owner_set__phone_number__icontains=search_query) |
                Q(owner_set__kra_pin__icontains=search_query) |
                Q(unit_type__icontains=search_query) |
                Q(status__icontains=search_query)
            ).distinct()
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filtered houses based on search
        houses = self.get_queryset()
        
        # Total houses in current filter
        context['houses_count'] = houses.count()
        
        # Houses with owners in current filter
        context['howned_count'] = houses.filter(status='owned').count()
        
        # Developer houses in current filter
        context['downed_count'] = houses.filter(status='developer').count()
        
        # Vacant houses in current filter
        context['vhouse_count'] = houses.filter(status='vacant').count()
        
        # Add search query to context for form
        context['search_query'] = self.request.GET.get('search', '')
        
        # Preserve search query in pagination links
        search_query = self.request.GET.get('search', '')
        context['search_query'] = search_query
        
        if search_query:
            context['extra_url_params'] = f'&search={search_query}'
        else:
            context['extra_url_params'] = ''

        return context

class HouseCreateView(LoginRequiredMixin, CreateView):
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
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['houses'] = House.objects.filter(
            Q(status='vacant') | Q(owner_set__isnull=True)
        ).order_by('hse_number')
        context['form'] = OwnerForm()
        context['total_owners'] = Owner.objects.count()
        return context

class OwnerCreateView(LoginRequiredMixin, CreateView):
    model = Owner
    form_class = OwnerForm
    success_url = reverse_lazy('owner-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Handle house assignment after owner is created
        house_id = self.request.POST.get('house')
        if house_id:
            house = House.objects.get(id=house_id)
            self.object.house.add(house)
            house.status = 'owned'
            house.save()
            
        messages.success(self.request, 'Owner created successfully.')
        return response

class OwnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Owner
    form_class = OwnerForm
    success_url = reverse_lazy('owner-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Owner updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error updating owner. Please check the form.')
        return super().form_invalid(form)

class OwnerDeleteView(LoginRequiredMixin, DeleteView):
    model = Owner
    template_name = 'owners/owner_confirm_delete.html'
    success_url = reverse_lazy('owner-list')