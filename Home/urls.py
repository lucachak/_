from django.urls import path
from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="home"),
    path("about/", views.About.as_view(), name="about"),
    path("princing/", views.Pricing.as_view(), name="pricing"),
    path("services/", views.Services.as_view(), name='services'),
    path('search/', views.Search.as_view(), name='search')
] 
