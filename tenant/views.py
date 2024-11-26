from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Exists, OuterRef
from .models import Tenant, Household, Tenancy
from house.models import House
from .forms import TenantForm, HouseholdForm, TenancyForm
from django.http import JsonResponse

class TenantListView(LoginRequiredMixin, ListView):
    model = Tenant
    template_name = 'tenant/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Tenant.objects.all()
        
        # Handle search
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(middle_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(id_cardnumber__icontains=search_query)
            )
        
        # Handle status filter
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get available houses (those without active tenancies)
        context['available_houses'] = House.objects.filter(
            ~Exists(
                Tenancy.objects.filter(
                    house=OuterRef('pk'),
                    end_date__isnull=True
                )
            ),
        ).order_by('hse_number')
        
        # Count statistics
        context['active_count'] = Tenant.objects.filter(status='active').count()
        context['notice_count'] = Tenant.objects.filter(status='notice').count()
        context['ended_count'] = Tenant.objects.filter(status='ended').count()
        context['household_count'] = Household.objects.filter(
            tenancy__end_date__isnull=True
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
        form.instance.status = 'active'
        response = super().form_valid(form)
        messages.success(self.request, 'Tenant added successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add tenant. Please check the form.')
        return super().form_invalid(form)

class TenantDetailView(LoginRequiredMixin, DetailView):
    model = Tenant
    template_name = 'tenant/tenant_detail.html'
    context_object_name = 'tenant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['household_form'] = HouseholdForm()
        context['current_tenancy'] = self.object.get_current_tenancy()
        context['tenancy_history'] = self.object.tenancy_set.all().order_by('-start_date')
        context['households'] = Household.objects.filter(
            tenancy__tenant=self.object
        ).order_by('-created_at')
        context['form'] = TenantForm(instance=self.object)
        context['tenancy_form'] = TenancyForm()
        
        # If editing, add the household to context
        household_id = self.request.GET.get('edit_household')
        if household_id:
            context['household'] = get_object_or_404(Household, pk=household_id)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        action = request.POST.get('action')
        
        if action == 'update_status':
            status = request.POST.get('status')
            self.object.status = status
            
            # Handle ending tenancy
            if status == 'ended':
                current_tenancy = self.object.get_current_tenancy()
                if current_tenancy:
                    current_tenancy.end_tenancy()
            
            self.object.save()
            messages.success(request, f'Tenant status updated to {status}.')
            
        elif action == 'end_tenancy':
            current_tenancy = self.object.get_current_tenancy()
            if current_tenancy:
                current_tenancy.end_tenancy()
            messages.success(request, 'Tenancy ended successfully.')
        
        elif action == 'create_tenancy':
            tenancy_form = TenancyForm(request.POST)
            if tenancy_form.is_valid():
                tenancy = tenancy_form.save(commit=False)
                tenancy.tenant = self.object
                tenancy.created_by = request.user
                tenancy.save()
                messages.success(request, 'New tenancy created successfully.')
            else:
                messages.error(request, 'Failed to create tenancy. Please check the form.')
        
        return redirect('tenant-detail', pk=self.object.pk)

class TenantUpdateView(LoginRequiredMixin, UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = 'tenant/tenant_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tenancy'] = self.object.get_current_tenancy()
        context['tenancy_history'] = self.object.tenancy_set.all().order_by('-start_date')
        context['households'] = Household.objects.filter(
            tenancy__tenant=self.object
        ).order_by('-created_at')
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tenant updated successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to update tenant. Please check the form.')
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('tenant-detail', kwargs={'pk': self.object.pk})

class HouseholdCreateView(LoginRequiredMixin, CreateView):
    model = Household
    form_class = HouseholdForm
    
    def form_valid(self, form):
        tenant = get_object_or_404(Tenant, pk=self.kwargs['tenant_pk'])
        current_tenancy = tenant.get_current_tenancy()
        
        if not current_tenancy:
            messages.error(self.request, 'Cannot add household member - no active tenancy.')
            return redirect('tenant-detail', pk=self.kwargs['tenant_pk'])
        
        household = form.save(commit=False)
        household.tenancy = current_tenancy
        household.created_by = self.request.user
        household.save()
        
        messages.success(self.request, 'Household member added successfully.')
        return redirect('tenant-detail', pk=self.kwargs['tenant_pk'])
    
    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add household member. Please check the form.')
        return redirect('tenant-detail', pk=self.kwargs['tenant_pk'])
    
    def get_success_url(self):
        return reverse_lazy('tenant-detail', kwargs={'pk': self.kwargs['tenant_pk']})

    def get(self, request, *args, **kwargs):
        return redirect('tenant-detail', pk=self.kwargs['tenant_pk'])

class HouseholdUpdateView(LoginRequiredMixin, UpdateView):
    model = Household
    form_class = HouseholdForm
    
    def get_success_url(self):
        return reverse_lazy('tenant-detail', kwargs={'pk': self.object.tenancy.tenant.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Household member updated successfully.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Failed to update household member. Please check the form.')
        return redirect('tenant-detail', pk=self.object.tenancy.tenant.pk)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = {
            'household': self.object,
            'tenant': self.object.tenancy.tenant
        }
        return JsonResponse({
            'id': self.object.id,
            'first_name': self.object.first_name,
            'last_name': self.object.last_name,
            'email': self.object.email,
            'phone_number': self.object.phone_number,
            'id_cardnumber': self.object.id_cardnumber,
            'nationality': self.object.nationality,
            'address': self.object.address
        })