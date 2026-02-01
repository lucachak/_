from django.urls import path
from . import views
# urls.py
urlpatterns = [
    path('pagamento/<int:order_id>/', views.process_payment, name='process_payment'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('sucesso/', views.payment_success, name='payment_success'),
    path('cancelado/', views.payment_cancel, name='payment_cancel'), # Adicione esta linha!
]
