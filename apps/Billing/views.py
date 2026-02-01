import stripe  # import mercadopago <-- Comentei também
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from Orders.models import Order
from django.views.decorators.csrf import csrf_exempt
import time # Para simular um tempinho de processamento
from .models import Invoice, Payment

stripe.api_key = settings.STRIPE_SK
# mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, client__user=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method == 'CARD':
            try:
                # Criando a sessão no Stripe
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'brl', # Valorizando seu plano para a Irlanda
                            'product_data': {'name': f'Pedido #{order.id}'},
                            'unit_amount': int(order.total_amount * 100),
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri('/billing/sucesso/'),
                    cancel_url=request.build_absolute_uri(f'/billing/pagamento/{order.id}/'),
                    metadata={'order_id': order.id}
                )

                # Se o request veio do HTMX, enviamos o header de redirecionamento
                if request.headers.get('HX-Request'):
                    response = HttpResponse(status=204)
                    response['HX-Redirect'] = checkout_session.url
                    return response
                
                return redirect(checkout_session.url, code=303)
            except Exception as e:
                return HttpResponse(f"Erro Real do Stripe: {str(e)}", status=500)
    
    return render(request, 'billing/checkout.html', {'order': order})



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_payment_success(session)

    return HttpResponse(status=200)

def handle_payment_success(session):
    order_id = session.get('metadata', {}).get('order_id')
    amount_total = session.get('amount_total') / 100 # Converte centavos para Euro/Real
    
    # Busca a Invoice vinculada ao Pedido
    invoice = Invoice.objects.get(order_id=order_id)
    
    # Cria o registro de pagamento no seu banco
    Payment.objects.create(
        invoice=invoice,
        amount=amount_total,
        method='CC',
        stripe_checkout_id=session.get('id'),
        transaction_id=session.get('payment_intent')
    )
    
    # Atualiza o status da fatura
    invoice.is_paid = True
    invoice.save()
    
    # Atualiza o pedido (lógica que você já tem no Orders)
    invoice.order.status = 'PAID' # Exemplo
    invoice.order.save()


def payment_success(request):
    """
    Página exibida após o redirecionamento positivo do Stripe.
    """
    # Dica de CS: Você pode passar o session_id via GET para buscar detalhes
    # Mas para um MVP impecável, apenas confirmar o sucesso já basta.
    return render(request, 'billing/success.html', {
        'title': 'Pagamento Confirmado!',
        'message': 'Recebemos seu pagamento. O status da sua bike será atualizado em instantes.'
    })

def payment_cancel(request):
    """
    Caso o usuário desista ou o cartão seja recusado antes de finalizar.
    """
    return render(request, 'billing/cancel.html', {
        'title': 'Pagamento Não Concluído',
        'message': 'O processo de pagamento foi interrompido. Nenhuma cobrança foi realizada.'
    })
