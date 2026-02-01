from django.urls import path
from . import views

urlpatterns = [
# A URL que exibe o checkout (escolha)
    path('pagamento/<int:order_id>/', views.process_payment, name='process_payment'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'), # Adicione esta linha   
    # URL de retorno do Stripe
    path('sucesso/', views.payment_success, name='payment_success'),
] 
