from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from .models import Product, Category
from .forms import ProductForm, TechnicalSpecForm

# --- CATALOGO (Mantendo sua CLASSE) ---
class Bikes(View):
    def get(self, request, *args, **kwargs):
        # 1. Base Query
        queryset = Product.objects.filter(
            product_type='BIKE', 
            ownership='SHOP', 
            is_active=True
        ).select_related('category', 'specs').order_by('-is_featured', '-created_at')

        # --- FILTROS (Seu código original mantido) ---
        category_val = request.GET.get('category')
        if category_val:
            queryset = queryset.filter(category__name__icontains=category_val)

        price_val = request.GET.get('price')
        if price_val:
            if '+' in price_val:
                min_price = price_val.replace('+', '').replace('.', '')
                queryset = queryset.filter(selling_price__gte=min_price)
            elif '-' in price_val:
                parts = price_val.split('-')
                if len(parts) == 2:
                    queryset = queryset.filter(selling_price__gte=parts[0], selling_price__lte=parts[1])

        range_val = request.GET.get('range')
        if range_val:
            if '80+' in range_val:
                queryset = queryset.filter(
                    Q(specs__range_estimate__icontains='80') | 
                    Q(specs__range_estimate__icontains='100') |
                    Q(specs__range_estimate__icontains='120')
                )
            else:
                try:
                    min_range = range_val.split('-')[0]
                    queryset = queryset.filter(specs__range_estimate__icontains=min_range)
                except:
                    pass

        tag_val = request.GET.get('tag')
        if tag_val == 'lancamento':
            queryset = queryset.filter(condition='NEW').order_by('-created_at')
        elif tag_val == 'promo':
            queryset = queryset.filter(selling_price__lt=4000)

        # --- ORDENAÇÃO ---
        sort_val = request.GET.get('sort')
        if sort_val == 'price_asc':
            queryset = queryset.order_by('selling_price')
        elif sort_val == 'price_desc':
            queryset = queryset.order_by('-selling_price')
        elif sort_val == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_val == 'popular':
            queryset = queryset.filter(is_featured=True)
        else:
            queryset = queryset.order_by('-is_featured', '-created_at')

        # --- PAGINAÇÃO ---
        paginator = Paginator(queryset, 8) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'bikes': page_obj,
            'total_count': queryset.count(),
            'categories': Category.objects.all(),
        }

        # --- CORREÇÃO VITAL DO HTMX ---
        # Se for HTMX (clique na paginação), retorna SÓ o grid parcial
        if request.headers.get('HX-Request'):
            return render(request, "partials/bikes_list.html", context)

        # Se for acesso normal, retorna a página completa (Pai)
        return render(request, "public/bike_catalog.html", context)


# --- DETALHES (Function View mantida conforme seu upload) ---
def bike_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category', 'specs').prefetch_related('images'), 
        pk=pk
    )
    
    related_queryset = Product.objects.filter(
        category=product.category, 
        is_active=True,
        ownership='SHOP'  # <--- ADICIONE ISSO
    ).exclude(pk=pk)
    
    if product.product_type == 'BIKE':
        related_queryset = related_queryset.filter(product_type='BIKE')
        
    related_products = related_queryset.order_by('?')[:3]

    context = {
        'bike': product,
        'related_bikes': related_products
    }
    
    return render(request, 'public/bike_detail.html', context)


# --- GESTÃO (ADD PRODUCT) ---
def add_product(request, fixed_type=None):
    # (Seu código da view de adicionar produto permanece igual ao anterior)
    page_title = "Novo Produto"
    if fixed_type == 'BIKE':
        page_title = "Cadastrar Nova Bike"
    elif fixed_type == 'COMPONENT':
        page_title = "Cadastrar Peça/Componente"
    elif fixed_type == 'SERVICE':
        page_title = "Cadastrar Serviço (Mão de Obra)"

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        spec_form = TechnicalSpecForm(request.POST)

        if product_form.is_valid():
            if fixed_type != 'SERVICE' and not spec_form.is_valid():
                messages.error(request, "Verifique os dados técnicos.")
            else:
                try:
                    with transaction.atomic():
                        product = product_form.save(commit=False)
                        if fixed_type:
                            product.product_type = fixed_type 
                        product.save()

                        if fixed_type != 'SERVICE':
                            spec = spec_form.save(commit=False)
                            spec.product = product
                            spec.save()

                        messages.success(request, f'{page_title} realizado com sucesso!')
                        return redirect('admin_dashboard') 
                except Exception as e:
                    messages.error(request, f'Erro ao salvar: {e}')
    else:
        initial_data = {}
        if fixed_type:
            initial_data['product_type'] = fixed_type
            
        product_form = ProductForm(initial=initial_data)
        spec_form = TechnicalSpecForm()

    context = {
        'product_form': product_form,
        'spec_form': spec_form,
        'fixed_type': fixed_type,
        'page_title': page_title
    }
    return render(request, 'staff/add_product_polymorphic.html', context)


# Adicione esta função simples
def cart_view(request):
    return render(request, 'public/cart.html')
