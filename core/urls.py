from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from Staff.views import AdminDashboardView, AdminReportsView, AdminSettingsView

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Staff / Admin Customizado
    path('dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('reports/', AdminReportsView.as_view(), name='admin_reports'),
    path('settings/', AdminSettingsView.as_view(), name='admin_settings'),

    # Apps Principais
    path("", include("Home.urls")),
    
    # CORREÇÃO: Padronizei para minúsculo "orders/"
    path('orders/', include('Orders.urls')), 
    
    path("billing/", include("Billing.urls")),
    
    path("staff/", include("Staff.urls")),
    path("clients/", include("Clients.urls")),
    
    # CORREÇÃO: Removida a duplicidade de 'accounts'
    path("accounts/", include("Accounts.urls")),
    
    path("assets/", include("Assets.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)