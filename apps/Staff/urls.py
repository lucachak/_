from django.urls import path
from . import views

urlpatterns = [
    # Dashboard Principal
    path("dashboard/", views.AdminDashboardView.as_view(), name="staff_dashboard"),
    
    # Gestão de Pedidos -- NOME CORRIGIDO AQUI EMBAIXO --
    path("orders/", views.StaffOrderListView.as_view(), name="staff_order_list"),
    path('pedido/<int:pk>/detalhes/', views.StaffOrderDetailView.as_view(), name='staff_order_detail'),
    path('pedido/<int:pk>/mudar-status/', views.staff_change_order_status, name='staff_change_status'),
    
    # Outras áreas
    path("customers/", views.Customers.as_view(), name="staff_customers"),
    path("reports/", views.AdminReportsView.as_view(), name="admin_reports"),
    path("settings/", views.AdminSettingsView.as_view(), name="admin_settings"),
]