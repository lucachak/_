from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Sum, Count, F, Avg, Q
from django.db.models.functions import TruncMonth, Coalesce
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy
import json
from django.contrib.admin.views.decorators import staff_member_required
import datetime
from django.utils import timezone
from django.db.models.functions import TruncDate

# Importe os seus models
from Orders.models import Order, OrderItem
from Assets.models import Product, TechnicalSpec, Maintenance
from Assets.forms import ProductForm, TechnicalSpecForm
from Clients.models import Client
from .mixins import StaffRequiredMixin
from .models import SiteConfiguration
from .forms import SiteSettingsForm


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'admin/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = timezone.now().date()
        start_of_month = today.replace(day=1)

        # --- 1. CARTÕES (KPIs Rápidos) ---
        
        # Vendas Hoje
        sales_today_data = Order.objects.filter(
            created_at__date=today, 
            status__in=['APPROVED', 'SENT', 'DELIVERED']
        ).aggregate(Sum('total_amount'))
        context['sales_today'] = sales_today_data['total_amount__sum'] or 0

        # Produtos Vendidos (Mês)
        products_sold_data = OrderItem.objects.filter(
            order__created_at__date__gte=start_of_month,
            order__status__in=['APPROVED', 'SENT', 'DELIVERED']
        ).aggregate(Sum('quantity'))
        context['products_sold_month'] = products_sold_data['quantity__sum'] or 0

        # Manutenção Ativa
        context['active_maintenance'] = Maintenance.objects.exclude(status='DELIVERED').count()

        # Estoque Crítico
        context['low_stock_count'] = Product.objects.filter(stock_quantity__lte=F('min_stock_alert')).count()

        # --- 2. GRÁFICO DE VENDAS (Últimos 6 Meses) ---
        six_months_ago = timezone.now() - datetime.timedelta(days=180)
        
        # Agrupa vendas por mês
        monthly_sales = (
            Order.objects.filter(created_at__gte=six_months_ago, status__in=['APPROVED', 'SENT', 'DELIVERED'])
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('total_amount'))
            .order_by('month')
        )

        # Prepara dados para o Chart.js (JSON)
        chart_labels = [x['month'].strftime('%b/%Y') for x in monthly_sales]
        chart_data = [float(x['total']) for x in monthly_sales]
        
        context['revenue_chart_labels'] = json.dumps(chart_labels)
        context['revenue_chart_data'] = json.dumps(chart_data)

        # --- 3. TABELAS E LISTAS ---
        context['recent_orders'] = Order.objects.select_related('client__user').order_by('-created_at')[:5]
        
        context['top_products'] = (
            OrderItem.objects
            .values('product__name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:4]
        )

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
        # Usa os novos métodos inteligentes do modelo
        if new_status == 'APPROVED':
            order.approve_payment()
            messages.success(request, f"Pedido #{order.id} aprovado e estoque atualizado!")
            
        elif new_status == 'CANCELED':
            order.cancel_order()
            messages.success(request, f"Pedido #{order.id} cancelado e estoque estornado!")
            
        else:
            # Para outros status (SENT, DELIVERED), apenas salva
            order.status = new_status
            order.save()
            messages.success(request, f"Status atualizado para {order.get_status_display()}")

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Erro ao atualizar: {e}")

    return redirect('staff_order_detail', pk=pk) # Certifique-se que o nome da url está correto
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
            .annotate(day=TruncDate('created_at')) # MUDANÇA AQUI
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
            # ERRO ERA AQUI: Mudado de 'order' para 'orders'
            total_orders=Count('orders'),
            
            # E AQUI TAMBÉM: Mudado 'order__...' para 'orders__...'
            total_spent=Coalesce(
                Sum('orders__total_amount', filter=Q(orders__status__in=['APPROVED', 'SENT', 'DELIVERED'])), 
                0.0,
                output_field=models.DecimalField()
            )
        ).order_by('-total_spent')



@staff_member_required
def add_product(request, fixed_type):
    """
    View polimórfica para adicionar produtos.
    fixed_type: 'BIKE', 'COMPONENT', 'SERVICE', etc.
    """
    # 1. Define títulos amigáveis
    titles = {
        'BIKE': 'Cadastrar Nova Bicicleta',
        'COMPONENT': 'Cadastrar Peça/Componente',
        'KIT': 'Cadastrar Kit de Conversão',
        'SERVICE': 'Cadastrar Serviço',
        'ACCESSORY': 'Cadastrar Acessório'
    }
    page_title = titles.get(fixed_type, 'Novo Produto')

    # 2. Processamento POST
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        spec_form = TechnicalSpecForm(request.POST)

        # Validação inicial do produto
        if product_form.is_valid():
            # Se NÃO for serviço, valida também a ficha técnica
            if fixed_type != 'SERVICE' and not spec_form.is_valid():
                messages.error(request, "Verifique os dados da Ficha Técnica.")
            else:
                try:
                    with transaction.atomic():
                        # A. Salva o Produto
                        product = product_form.save(commit=False)
                        product.product_type = fixed_type  # Força o tipo da URL
                        product.ownership = 'SHOP'         # Força ser da Loja
                        product.save()

                        # B. Salva a Ficha Técnica (se não for serviço)
                        if fixed_type != 'SERVICE':
                            spec = spec_form.save(commit=False)
                            spec.product = product
                            spec.save()
                        
                        # C. Salva imagens da galeria (se houver, lógica extra aqui)
                        
                        messages.success(request, f"{product.name} cadastrado com sucesso!")
                        return redirect('staff_dashboard')

                except Exception as e:
                    messages.error(request, f"Erro ao salvar no banco: {e}")
        else:
            messages.error(request, "Corrija os erros no formulário principal.")
    
    # 3. Carregamento Inicial (GET)
    else:
        product_form = ProductForm(initial={'product_type': fixed_type})
        spec_form = TechnicalSpecForm()

    context = {
        'product_form': product_form,
        'spec_form': spec_form,
        'page_title': page_title,
        'fixed_type': fixed_type
    }
    
    return render(request, 'staff/add_product.html', context)