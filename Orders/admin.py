from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display # Helper para badges
from .models import Order, OrderItem, OrderTimeline

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1
    tab = True # Cria uma aba separada dentro do pedido (Visual limpo)

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'client', 'show_status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at') # O Unfold cria filtros laterais bonitos auto
    search_fields = ('client__user__email', 'id')
    
    inlines = [OrderItemInline]

    # BADGES COLORIDOS
    @display(
        description="Status",
        label={
            'QUOTE': 'info',      # Azul
            'APPROVED': 'primary', # Roxo
            'IN_PROGRESS': 'warning', # Amarelo (Oficina trabalhando)
            'READY': 'success',   # Verde
            'FINISHED': 'success',
            'CANCELED': 'danger', # Vermelho
        }
    )
    def show_status(self, obj):
        return obj.status
