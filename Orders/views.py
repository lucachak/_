from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from Assets.models import Product
from .cart import Cart 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Order, OrderItem,Coupon
from Clients.models import Client 

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
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
    
    # 1. Se carrinho estiver vazio, não deixa prosseguir
    if len(cart) == 0:
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('bike_catalog')

    # 2. Busca ou Cria o Perfil de Cliente
    try:
        # Tenta pegar o cliente existente
        client = request.user.client
    except:
        # Se não existir, cria um novo APENAS com o user.
        # Removemos 'name' e 'email' daqui porque eles já ficam no request.user
        client = Client.objects.create(
            user=request.user
        )
        
    # --- TRAVA DE ENDEREÇO ---
    if not client.is_complete():
        messages.warning(request, "Por favor, complete seu Endereço e CPF para finalizar a compra.")
        
        # LÓGICA DO NEXT: Monta a URL de perfil + o parâmetro next apontando de volta pra cá
        checkout_url = reverse('checkout_create_order')
        profile_url = reverse('client_profile')
        return redirect(f"{profile_url}?next={checkout_url}")
    # -------------------------



    # 3. Cria o Pedido (Order) no Banco
    order = Order.objects.create(
        client=client,
        status='QUOTE', 
        total_amount=cart.get_total_price_after_discount()
    )

    # 4. Transfere os itens do Carrinho para o Banco (OrderItem)
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            unit_price=item['price'],
            description=item['product'].name
        )

    # 5. Limpa o carrinho da sessão
    cart.clear()
    
    print(f"✅ Pedido #{order.id} criado com sucesso! Redirecionando...")

    # 6. Redireciona para o Pagamento
    return redirect('process_payment', order_id=order.id)


@login_required
def client_orders(request):
    # Busca pedidos do cliente logado, ordenados do mais recente para o mais antigo
    # O 'prefetch_related' otimiza para buscar os itens junto e não travar o banco
    orders = Order.objects.filter(client__user=request.user).prefetch_related('items__product').order_by('-created_at')
    
    return render(request, 'public/client_orders.html', {'orders': orders})



@require_POST
def coupon_apply(request):
    code = request.POST.get('code')
    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        request.session['coupon_id'] = coupon.id # Salva na sessão
        messages.success(request, "Cupom aplicado com sucesso!")
    except Coupon.DoesNotExist:
        request.session['coupon_id'] = None
        messages.error(request, "Cupom inválido ou expirado.")
    
    return redirect('cart_detail')