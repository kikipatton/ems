from django.urls import path
from . import views

urlpatterns = [
    path('house/<int:pk>/meter/', views.HouseMeterView.as_view(), name='house-meter'),
    path('house/<int:house_pk>/meter/create/', views.MeterCreateView.as_view(), name='meter-create'),
    path('meter/<int:pk>/replace/', views.MeterReplaceView.as_view(), name='meter-replace'),
    path('meter/<int:meter_pk>/reading/', views.ReadingCreateView.as_view(), name='reading-create'),
]