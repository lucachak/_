from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.db import transaction

from .models import Product, Category
from .forms import ProductForm, TechnicalSpecForm

# --- CATÁLOGO PÚBLICO ---

class Bikes(View):
    def get(self, request, *args, **kwargs):
        # 1. Captura o parâmetro da URL (Vem 'BIKE' ou 'PART')
        product_type_param = request.GET.get('product_type', 'BIKE')
        
        # 2. Inicia a Query Base (Apenas produtos da loja e ativos)
        queryset = Product.objects.filter(
            ownership='SHOP', 
            is_active=True
        ).select_related('category', 'specs').prefetch_related('images')
        
        # 3. LÓGICA CORRIGIDA: Mapeia o filtro da URL para os tipos do Banco
        if product_type_param == 'PART':
            # Se selecionou "Peças", traz Componentes, Kits e Acessórios
            # (Exclui BIKE e SERVICE)
            queryset = queryset.filter(product_type__in=['COMPONENT', 'KIT', 'ACCESSORY'])
        else:
            # Padrão: Traz apenas Bicicletas
            queryset = queryset.filter(product_type='BIKE')
        
        # --- FILTROS ADICIONAIS (Busca, Categoria, Condição, etc.) ---
        search_query = request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )

        category_val = request.GET.get('category')
        if category_val:
            # Filtra pelo nome da categoria (ex: Mountain Bike, Elétrica, etc)
            queryset = queryset.filter(category__name=category_val)

        condition_val = request.GET.get('condition')
        if condition_val in ['NEW', 'USED']:
            queryset = queryset.filter(condition=condition_val)

        # --- ORDENAÇÃO ---
        ordering_val = request.GET.get('ordering')
        
        if ordering_val == 'price_asc':
            queryset = queryset.order_by('selling_price')
        elif ordering_val == 'price_desc':
            queryset = queryset.order_by('-selling_price')
        elif ordering_val == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-is_featured', '-created_at')

        # --- PAGINAÇÃO ---
        paginator = Paginator(queryset, 9) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Helper para URL
        params = request.GET.copy()
        if 'page' in params:
            del params['page']

        context = {
            'bikes': page_obj,
            'total_count': queryset.count(),
            'categories': Category.objects.all(),
            'current_params': params.urlencode(),
            'active_type': product_type_param 
        }

        if request.headers.get('HX-Request'):
            return render(request, "partials/bikes_list.html", context)

        return render(request, "public/bike_catalog.html", context)

def bike_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category', 'specs').prefetch_related('images'), 
        pk=pk
    )
    
    # Busca relacionados da mesma categoria
    related_queryset = Product.objects.filter(
        category=product.category, 
        is_active=True,
        ownership='SHOP' 
    ).exclude(pk=pk)
    
    # Filtra pelo mesmo tipo (Se estou vendo peça, mostre peças relacionadas)
    related_queryset = related_queryset.filter(product_type=product.product_type)
        
    related_products = related_queryset.order_by('?')[:3]

    context = {
        'bike': product,
        'related_bikes': related_products
    }
    
    return render(request, 'public/bike_detail.html', context)


# --- ÁREA ADMINISTRATIVA (STAFF) ---

def add_product(request, fixed_type=None):
    page_title = "Novo Produto"
    if fixed_type == 'BIKE':
        page_title = "Cadastrar Nova Bike"
    elif fixed_type == 'COMPONENT' or fixed_type == 'PART':
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
                        return redirect('admin_dashboard') # Certifique-se que essa URL existe
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