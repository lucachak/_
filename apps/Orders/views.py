from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import transaction  
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from Assets.models import Product
from Clients.models import Client 
# IMPORTANTE: Remova "from .cart import Cart" se ainda tiver
from .models import Order, OrderItem, Coupon, Cart, CartItem

def _get_cart(request):
    """
    Função auxiliar interna: Recupera o carrinho do BD (Usuário ou Sessão).
    """
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key

    if request.user.is_authenticated:
        # Tenta pegar pelo cliente logado
        try:
            client, created = Client.objects.get_or_create(user=request.user)
            cart, created = Cart.objects.get_or_create(user=client)
        except Exception:
            # Fallback se algo der errado com o Client
            cart, created = Cart.objects.get_or_create(session_key=session_key)
    else:
        # Visitante anônimo
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    
    return cart

def cart_detail(request):
    cart = _get_cart(request)

    items = cart.items.select_related('product').all()

    return render(request, 'public/cart.html', {'cart': cart, 'items': items})

def cart_add(request, product_id): # Renomeei para cart_add para bater com seu padrão
    """Adiciona item ao carrinho (Model)."""
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Busca ou cria o item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # Validação de Estoque Simples
    nova_quantidade = cart_item.quantity + 1 if not created else 1
    
    if nova_quantidade > product.stock_quantity:
         messages.warning(request, f"Estoque limite atingido para {product.name}!")
    else:
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Mais uma unidade de {product.name} adicionada.")
        else:
            # Item novo já vem com qtd 1 por default no model
            messages.success(request, f"{product.name} adicionado ao carrinho!")
        
    return redirect('cart_detail')

def cart_remove(request, product_id):
    """Remove item do carrinho."""
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    CartItem.objects.filter(cart=cart, product=product).delete()
    messages.info(request, "Item removido.")
    
    return redirect('cart_detail')

@require_POST
def coupon_apply(request):
    """Aplica cupom ao carrinho (Salva no Model Cart)."""
    code = request.POST.get('code')
    cart = _get_cart(request)
    
    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        cart.coupon = coupon
        cart.save()
        messages.success(request, f"Cupom {coupon.code} aplicado!")
    except Coupon.DoesNotExist:
        cart.coupon = None
        cart.save()
        messages.error(request, "Cupom inválido ou expirado.")
    
    return redirect('cart_detail')

@login_required
def checkout_create_order(request):
    """Transforma o Carrinho (Model) em um Pedido (Order)."""
    cart = _get_cart(request)
    
    # Verifica se tem itens usando .exists()
    if not cart.items.exists():
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('bike_catalog')

    client, created = Client.objects.get_or_create(user=request.user)
        
    if not client.is_complete():
        messages.warning(request, "Por favor, complete seu Endereço e CPF para finalizar a compra.")
        checkout_url = reverse('checkout_create_order')
        profile_url = reverse('client_profile') # Ajuste se sua rota for diferente
        return redirect(f"{profile_url}?next={checkout_url}")

    try:
        with transaction.atomic():
            # 1. Cria o Pedido
            order = Order.objects.create(
                client=client,
                status='QUOTE', 
                coupon=cart.coupon, # Transfere o cupom do carrinho pro pedido
                # O total será recalculado no update_total(), mas podemos salvar inicial
                total_amount=0 
            )

            # 2. Transfere Itens do Carrinho -> Itens do Pedido
            for cart_item in cart.items.all():
                product = cart_item.product
                qty = cart_item.quantity
                
                # Bloqueia produto no banco para evitar race condition
                product_in_db = Product.objects.select_for_update().get(id=product.id)
                
                if product_in_db.stock_quantity < qty:
                    raise ValueError(f"Desculpe, o produto {product.name} acabou de esgotar.")

                # Cria o item do pedido (snapshot do preço acontece no save() do model)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    # unit_price será pego automaticamente do produto se omitido, 
                    # mas podemos forçar se quisermos garantir
                )
            
            # 3. Calcula total final do pedido
            order.update_total()
            
            # 4. Limpa o carrinho (apaga itens e remove cupom)
            cart.items.all().delete()
            cart.coupon = None
            cart.save()
            
            return redirect('process_payment', order_id=order.id)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart_detail')
        
    except Exception as e:
        messages.error(request, "Ocorreu um erro técnico. Tente novamente.")
        print(f"Erro Crítico Checkout: {e}") 
        return redirect('cart_detail')

@login_required
def client_orders(request):
    orders = Order.objects.filter(client__user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'public/client_orders.html', {'orders': orders})