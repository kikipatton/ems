from django.urls import path
from . import views

urlpatterns = [
    # House URLs
    path('houses/', views.HouseListView.as_view(), name='house-list'),
    path('house/new/', views.HouseCreateView.as_view(), name='house-create'),
    path('house/<int:pk>/', views.HouseDetailView.as_view(), name='house-detail'),
    path('house/<int:pk>/update/', views.HouseUpdateView.as_view(), name='house-update'),
    path('house/<int:pk>/delete/', views.HouseDeleteView.as_view(), name='house-delete'),
    
    # Owner URLs
    path('owners/', views.OwnerListView.as_view(), name='owner-list'),
    path('owner/new/',views.OwnerCreateView.as_view(), name='owner-create'),
    path('owner/<int:pk>/update/', views.OwnerUpdateView.as_view(), name='owner-update'),
    path('owners/<int:pk>/delete/', views.OwnerDeleteView.as_view(), name='owner-delete'),
    
    # Garbageurl
    path('house/<int:pk>/garbage-collection/', views.GarbageCollectionUpdateView.as_view(), name='garbage-collection'),
]