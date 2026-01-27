from django.contrib import admin
from django.urls import include, path

from . import views

# Create your views here.
urlpatterns =[
        path("dashboard/", views.Dashboard.as_view(), name="client_dashboard"),
        path("billing/",views.Billing.as_view(), name="client_billing"),
        path("settings/", views.ClientSettings.as_view(), name="client_settings"),
        path('meus-dados/', views.ProfileView.as_view(), name='client_profile'),

        path('agendar/', views.schedule_appointment, name='client_scheduler'),
        path('api/calendar/', views.api_appointments, name='api_appointments'),
        ]
