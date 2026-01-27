# import stripe  <-- Comentei para não dar erro se não tiver instalado
# import mercadopago <-- Comentei também
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from Orders.models import Order
import time # Para simular um tempinho de processamento

# --- MODO SIMULAÇÃO (Sem chaves reais) ---
# stripe.api_key = settings.STRIPE_SECRET_KEY
# mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
def process_payment(request, order_id):
    # Garante que o pedido é do usuário logado
    order = get_object_or_404(Order, id=order_id, client__user=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        try:
            time.sleep(1) # Simulação de delay

            # --- CORREÇÃO AQUI: Usar 'CARD' (Maiúsculo) ---
            if payment_method == 'CARD': 
                print(f"💰 [SIMULAÇÃO] Cartão Aprovado para Pedido #{order.id}")
                
                # CHAMA O NOVO MÉTODO DO MODELO
                try:
                    order.approve_payment()
                    return redirect('payment_success') # Sucesso!
                except ValueError as e:
                    messages.error(request, str(e)) # Erro de estoque
                    return redirect('cart_detail')

            # --- CORREÇÃO AQUI: Usar 'PIX' (Maiúsculo) ---
            elif payment_method == 'PIX': 
                
                fake_qr_code = "00020126580014BR.GOV.BCB.PIX..."
                # Imagem de exemplo
                fake_qr_image = "https://upload.wikimedia.org/wikipedia/commons/d/d0/QR_code_for_mobile_English_Wikipedia.svg"

                return render(request, 'billing/pix_payment.html', {
                    'qr_code': fake_qr_code,
                    'qr_image': fake_qr_image,
                    'order': order
                })
        
        except Exception as e:
            messages.error(request, f"Erro: {str(e)}")

    return render(request, 'billing/checkout.html', {'order': order})

def payment_success(request):
    # Crie um template simples 'billing/success.html' depois
    return render(request, 'billing/success.html')