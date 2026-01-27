from django.urls import include, path

from . import views
 
urlpatterns = [
    path("bikes/", views.Bikes.as_view(), name="bike_catalog"),
    path('produto/<int:pk>/', views.bike_detail, name='bike_detail'),
    path('staff/novo-produto/', views.add_product, name='add_product'),
    #path('carrinho/', views.cart_view, name='cart_detail'),    # Usamos a mesma view 'add_product', mas passamos um parâmetro fixo no dicionário
    path('staff/novo/bike/', views.add_product, {'fixed_type': 'BIKE'}, name='add_bike'),
    path('staff/novo/componente/', views.add_product, {'fixed_type': 'COMPONENT'}, name='add_component'),
    path('staff/novo/servico/', views.add_product, {'fixed_type': 'SERVICE'}, name='add_service'),
    
    # Rota genérica (caso precise)
    path('staff/novo/geral/', views.add_product, name='add_product_general'),
    ]
