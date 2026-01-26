from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.db import transaction  # <--- FALTAVA ISTO AQUI!
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from Assets.models import Product
from Clients.models import Client 
from .models import Order, OrderItem, Coupon
from .cart import Cart 

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Tenta adicionar (captura se atingiu o limite)
    limit_reached = cart.add(product=product, quantity=1)
    
    if limit_reached:
        messages.warning(request, f"Estoque limitado! Adicionamos o máximo disponível de {product.name}.")
    else:
        messages.success(request, f"{product.name} adicionado ao carrinho!")
        
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'public/cart.html', {'cart': cart})

@login_required
def checkout_create_order(request):
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('bike_catalog')

    # Busca ou Cria o Cliente
    client, created = Client.objects.get_or_create(user=request.user)
        
    if not client.is_complete():
        messages.warning(request, "Por favor, complete seu Endereço e CPF para finalizar a compra.")
        checkout_url = reverse('checkout_create_order')
        profile_url = reverse('client_profile')
        return redirect(f"{profile_url}?next={checkout_url}")

    # --- INÍCIO DA TRANSAÇÃO ATÔMICA ---
    try:
        with transaction.atomic():
            # 1. Cria o Pedido (Status inicial QUOTE)
            order = Order.objects.create(
                client=client,
                status='QUOTE', 
                total_amount=cart.get_total_price_after_discount()
            )

            # 2. Itera sobre o carrinho e cria os itens
            for item in cart:
                product = item['product']
                qty = item['quantity']
                
                # 3. VALIDAÇÃO FINAL DE ESTOQUE (Anti-concorrência)
                # Verifica no banco a quantidade atual exata e trava a linha
                product_in_db = Product.objects.select_for_update().get(id=product.id)
                
                if product_in_db.stock_quantity < qty:
                    # Se faltar estoque na hora H, cancela tudo!
                    raise ValueError(f"Desculpe, o produto {product.name} acabou de esgotar.")

                # Cria o item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    unit_price=item['price'],
                    description=product.name
                )
                
            # 4. Sucesso! Limpa o carrinho
            cart.clear()
            
            # 5. Redireciona para o Pagamento
            return redirect('process_payment', order_id=order.id)

    except ValueError as e:
        # Erro de validação (ex: estoque acabou)
        messages.error(request, str(e))
        return redirect('cart_detail')
        
    except Exception as e:
        # Erro técnico inesperado
        messages.error(request, "Ocorreu um erro ao processar seu pedido. Tente novamente.")
        print(f"Erro Crítico Checkout: {e}") # Log para debug
        return redirect('cart_detail')

@login_required
def client_orders(request):
    # Busca pedidos do cliente logado
    orders = Order.objects.filter(client__user=request.user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'public/client_orders.html', {'orders': orders})

@require_POST
def coupon_apply(request):
    code = request.POST.get('code')
    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        request.session['coupon_id'] = coupon.id 
        messages.success(request, "Cupom aplicado com sucesso!")
    except Coupon.DoesNotExist:
        request.session['coupon_id'] = None
        messages.error(request, "Cupom inválido ou expirado.")
    
    return redirect('cart_detail')