from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, FormView, View , UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Count, F, Avg, Q
from django.db.models.functions import TruncMonth, Coalesce
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
import json
import datetime
from django.utils import timezone

# Importe seus models
from Orders.models import Order, OrderItem
from Assets.models import Product
from Clients.models import Client
from .mixins import StaffRequiredMixin
from .models import SiteConfiguration
from .forms import SiteSettingsForm


# --- 1. DASHBOARD INTELIGENTE ---
class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- KPIS TOPO ---
        revenue_data = Order.objects.filter(status__in=['APPROVED', 'SENT', 'DELIVERED']).aggregate(Sum('total_amount'))
        context['total_revenue'] = revenue_data['total_amount__sum'] or 0
        
        context['total_orders'] = Order.objects.count()
        context['avg_ticket'] = Order.objects.filter(status='APPROVED').aggregate(Avg('total_amount'))['total_amount__avg'] or 0
        context['total_clients'] = Client.objects.count()

        # --- GRÁFICO 1: Faturamento Mensal (Últimos 6 meses) ---
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        monthly_sales = (
            Order.objects.filter(created_at__gte=six_months_ago, status__in=['APPROVED', 'SENT', 'DELIVERED'])
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )

        chart_labels = [x['month'].strftime('%b/%Y') for x in monthly_sales]
        chart_data = [float(x['total']) for x in monthly_sales]
        
        context['revenue_chart_labels'] = json.dumps(chart_labels)
        context['revenue_chart_data'] = json.dumps(chart_data)

        # --- GRÁFICO 2: Status dos Pedidos (Pizza) ---
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        status_map = dict(Order.STATUS_CHOICES)
        pie_labels = [status_map.get(x['status'], x['status']) for x in status_counts]
        pie_data = [x['count'] for x in status_counts]

        context['status_pie_labels'] = json.dumps(pie_labels)
        context['status_pie_data'] = json.dumps(pie_data)

        # --- LISTAS DETALHADAS ---
        context['top_products'] = (
            OrderItem.objects
            .values('product__name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:5]
        )

        # Estoque Crítico (<= 3 unidades)
        context['low_stock'] = Product.objects.filter(stock_quantity__lte=3, product_type__in=['BIKE', 'COMPONENT'])[:5]
        
        return context

# --- 2. GESTÃO DE PEDIDOS ---
class StaffOrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = 'staff/order_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']
    paginate_by = 20

    def get_queryset(self):
        return Order.objects.select_related('client__user').order_by('-created_at')

class StaffOrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = 'staff/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.prefetch_related('items__product', 'client__user')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def staff_change_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status')
    
    try:
        with transaction.atomic():
            old_status = order.status
            
            # Baixa estoque ao aprovar
            if new_status == 'APPROVED' and old_status != 'APPROVED':
                for item in order.items.all():
                    if item.product.product_type != 'SERVICE': 
                        if item.product.stock_quantity >= item.quantity:
                            item.product.stock_quantity -= item.quantity
                            item.product.save()
                        else:
                            raise ValueError(f"Estoque insuficiente: {item.product.name}")

            # Devolve estoque ao cancelar (se já estava aprovado)
            elif new_status == 'CANCELED' and old_status == 'APPROVED':
                for item in order.items.all():
                    if item.product.product_type != 'SERVICE':
                        item.product.stock_quantity += item.quantity
                        item.product.save()

            order.status = new_status
            order.save()
            messages.success(request, f"Pedido #{order.id} atualizado para {order.get_status_display()}")

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Erro crítico: {e}")

    return redirect('staff_order_detail', pk=pk)

# --- 3. RELATÓRIOS E CONFIGURAÇÕES ---
class AdminReportsView(StaffRequiredMixin, TemplateView):
    template_name = 'admin/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['sales_by_category'] = (
            OrderItem.objects
            .filter(order__status='APPROVED')
            .values('product__category__name')
            .annotate(
                qty_sold=Sum('quantity'),
                revenue=Sum(F('quantity') * F('unit_price'))
            )
            .order_by('-revenue')
        )

        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        context['daily_sales'] = (
            Order.objects.filter(created_at__gte=thirty_days_ago, status='APPROVED')
            .extra(select={'day': 'date(created_at)'})
            .values('day')
            .annotate(total=Sum('total_amount'), count=Count('id'))
            .order_by('-day')
        )
        return context


class AdminSettingsView(StaffRequiredMixin, UpdateView):
    model = SiteConfiguration
    form_class = SiteSettingsForm
    template_name = 'admin/settings.html'
    success_url = reverse_lazy('admin_settings')

    def get_object(self, queryset=None):
        # Garante que sempre pega a configuração ID=1 (Singleton)
        # Se não existir, cria uma nova agora.
        obj, created = SiteConfiguration.objects.get_or_create(pk=1)
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Configurações salvas com sucesso!")
        return super().form_valid(form)

class Customers(StaffRequiredMixin, ListView):
    model = Client
    template_name = "staff/customer_list.html"
    context_object_name = "clients"
    ordering = ['-user__date_joined']
    paginate_by = 20

    def get_queryset(self):
        # Busca clientes e anota dados de compras
        return Client.objects.select_related('user').annotate(
            total_orders=Count('order'),
            # Soma apenas pedidos APROVADOS. Se for Null (nunca comprou), vira 0.0
            total_spent=Coalesce(
                Sum('order__total_amount', filter=Q(order__status__in=['APPROVED', 'SENT', 'DELIVERED'])), 
                0.0,
                output_field=models.DecimalField()
            )
        ).order_by('-total_spent') #