# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Tenant URLs
    path('tenant', views.TenantListView.as_view(), name='tenant-list'),
    path('tenant/add/', views.TenantCreateView.as_view(), name='tenant-create'),
    path('tenant/<int:pk>/', views.TenantDetailView.as_view(), name='tenant-detail'),
    path('tenant/<int:pk>/update/', views.TenantUpdateView.as_view(), name='tenant-update'),
    
    # Household URLs
    path('tenant/<int:tenant_pk>/household/add/', 
         views.HouseholdCreateView.as_view(), name='household-create'),
    path('tenant/household/<int:pk>/update/', 
         views.HouseholdUpdateView.as_view(), name='household-update'),
]