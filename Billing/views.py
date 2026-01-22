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
    # Busca o pedido no banco
    order = get_object_or_404(Order, id=order_id) # Removi a trava de user pra facilitar testes se precisar

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        try:
            # Simula um pequeno delay de processamento
            time.sleep(1) 

            # --- SIMULAÇÃO STRIPE (CARTÃO) ---
            if payment_method == 'stripe':
                # Em vez de criar sessão no Stripe, aprovamos direto!
                print(f"💰 [SIMULAÇÃO] Pagamento via CARTÃO para Pedido #{order.id} iniciado.")
                
                # Redireciona direto para a tela de sucesso
                return redirect('payment_success')

            # --- SIMULAÇÃO PIX (MERCADO PAGO) ---
            elif payment_method == 'pix':
                print(f"💰 [SIMULAÇÃO] Pagamento via PIX para Pedido #{order.id} solicitado.")
                
                # Dados Fakes para o Template não quebrar
                fake_qr_code = "00020126580014BR.GOV.BCB.PIX0136123e4567-e12b-12d1-a456-426655440000520400005303986540510.005802BR5913EletricBike6008SaoPaulo62070503***6304E2CA"
                
                # Um quadrado cinza em Base64 para simular a imagem do QR Code
                fake_qr_image = "iVBORw0KGgoAAAANSUhEUgAAAMgAAADIAQMAAACX63O8AAAABlBMVEX///8AAABVwtN+AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAAJElEQVRYhe3BMQEAAADCoPVPbQ0PoAAAAAAAAAAAAAAAAAAAAHgMt8AAAd44Op8AAAAASUVORK5CYII="

                # Renderiza o template de PIX com os dados falsos
                return render(request, 'billing/pix_payment.html', {
                    'qr_code': fake_qr_code,
                    'qr_image': fake_qr_image,
                    'order': order
                })
        
        except Exception as e:
            messages.error(request, f"Erro na simulação: {str(e)}")

    # GET: Renderiza a tela de escolha (Checkout)
    return render(request, 'billing/checkout.html', {'order': order})

def payment_success(request):
    # Crie um template simples 'billing/success.html' depois
    return render(request, 'billing/success.html')