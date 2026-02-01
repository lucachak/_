from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Invoice, Payment, Refund

class PaymentInline(TabularInline):
    model = Payment
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ('invoice_number', 'due_date', 'paid_status', 'total_paid_display')
    list_filter = ('is_paid', 'due_date')
    inlines = [PaymentInline]

    @display(description="Pago?", boolean=True)
    def paid_status(self, obj):
        return obj.is_paid

    def total_paid_display(self, obj):
        # Faz a soma direto no Banco de Dados (SQL), muito mais rápido que sum() em Python
        total = obj.payments.aggregate(Sum('amount'))['amount__sum']
        return total or 0.00

    total_paid_display.short_description = "Total Recebido"

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('amount', 'method_badge', 'created_at', 'invoice')
    
    @display(
        description="Método",
        label={
            'PIX': 'success', # Pix é alegria (Verde)
            'CC': 'info',
            'CD': 'info',
            'CASH': 'warning', # Dinheiro requer atenção (Laranja)
        }
    )
    def method_badge(self, obj):
        return obj.method
