# views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from .models import Tenant, Household
from house.models import House
from .forms import TenantForm, HouseholdForm

class TenantListView(LoginRequiredMixin, ListView):
    model = Tenant
    template_name = 'tenant/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 10
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get available houses (those without active tenants)
        context['available_houses'] = House.objects.filter(
            Q(current_tenant__isnull=True) | 
            Q(current_tenant__status='ended') |
            Q(status='Vacant')
        ).order_by('hse_number')
        
        # Count statistics
        context['active_count'] = Tenant.objects.filter(status='active').count()
        context['notice_count'] = Tenant.objects.filter(status='notice').count()
        context['ended_count'] = Tenant.objects.filter(status='ended').count()
        context['household_count'] = Household.objects.filter(
            tenant__status='active'
        ).count()
        
        # Get status choices for filter
        context['status_choices'] = Tenant.STATUS_CHOICES
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Handle pagination parameters
        params = []
        if self.request.GET.get('search'):
            params.append(f'search={self.request.GET.get("search")}')
        if self.request.GET.get('status'):
            params.append(f'status={self.request.GET.get("status")}')
        context['extra_url_params'] = f'&{"&".join(params)}' if params else ''
        
        return context

class TenantCreateView(LoginRequiredMixin, CreateView):
    model = Tenant
    form_class = TenantForm
    success_url = reverse_lazy('tenant-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'active'  # Set default status for new tenants
        response = super().form_valid(form)
            
        messages.success(self.request, 'Tenant added successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add tenant. Please check the form.')
        return redirect('tenant-list')

class TenantDetailView(LoginRequiredMixin, DetailView):
    model = Tenant
    template_name = 'tenant/tenant_detail.html'
    context_object_name = 'tenant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['household_form'] = HouseholdForm()
        context['households'] = self.object.household_set.all()
        context['status_choices'] = Tenant.STATUS_CHOICES
        return context
    
    def post(self, request, *args, **kwargs):
        tenant = self.get_object()
        action = request.POST.get('action')
        
        if action == 'end_tenancy':
            # Update tenant status and end date
            tenant.status = 'ended'
            tenant.enddate_at = timezone.now()
            tenant.save()
            
            # Update house status
            if tenant.house:
                house = tenant.house
                house.status = 'vacant'
                house.save()
                
            messages.success(request, 'Tenancy ended successfully.')
            return redirect('tenant-list')
            
        return super().get(request, *args, **kwargs)

class TenantUpdateView(LoginRequiredMixin, UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'tenant/tenant_form.html'
    
    def get_success_url(self):
        return reverse_lazy('tenant-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle house status updates based on tenant status
        if self.object.status == 'ended':
            if self.object.house:
                self.object.house.status = 'vacant'
                self.object.house.save()
        elif self.object.status == 'active':
            if self.object.house:
                self.object.house.status = 'occupied'
                self.object.house.save()
                
        messages.success(self.request, 'Tenant updated successfully.')
        return response

# Household Views
class HouseholdCreateView(LoginRequiredMixin, CreateView):
    model = Household
    form_class = HouseholdForm
    template_name = 'tenant/household_form.html'
    
    def form_valid(self, form):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        form.instance.tenant = tenant
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Household member added successfully.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('tenant-detail', kwargs={'pk': self.kwargs['tenant_pk']})

class HouseholdUpdateView(LoginRequiredMixin, UpdateView):
    model = Household
    form_class = HouseholdForm
    template_name = 'tenant/household_form.html'
    
    def get_success_url(self):
        return reverse_lazy('tenant-detail', kwargs={'pk': self.object.tenant.pk})