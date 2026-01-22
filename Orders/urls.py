from django.urls import path
from . import views

urlpatterns = [
    path('carrinho/', views.cart_detail, name='cart_detail'),
    path('carrinho/adicionar/<int:product_id>/', views.cart_add, name='cart_add'),
    path('carrinho/remover/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('finalizar-compra/', views.checkout_create_order, name='checkout_create_order'),
    path('meus-pedidos/', views.client_orders, name='client_orders'),
    path('cupom/aplicar/', views.coupon_apply, name='coupon_apply'),
]