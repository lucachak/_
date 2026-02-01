from django.db import models
from Common.models import TimeStampedModel
from Orders.models import Order

class Invoice(TimeStampedModel):
    """
    Representa a cobrança (Fatura/Recibo) gerada a partir de um Pedido.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField("Nota Fiscal/Recibo", max_length=50, unique=True)
    due_date = models.DateField("Vencimento")
    is_paid = models.BooleanField("Pago?", default=False)

    def __str__(self):
        return f"Invoice {self.invoice_number} - Pedido #{self.order.id}"

class Payment(TimeStampedModel):
    """
    Registra cada transação financeira recebida para uma fatura.
    Uma fatura pode ter vários pagamentos (ex: entrada + parcelas).
    """
    METHOD_CHOICES = [
        ('PIX', 'Pix'),
        ('CC', 'Cartão Crédito'),
        ('CD', 'Cartão Débito'),
        ('CASH', 'Dinheiro'),
    ]
    stripe_checkout_id = models.CharField("ID Checkout Stripe", max_length=255, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField("Valor Pago", max_digits=10, decimal_places=2)
    method = models.CharField("Método", max_length=10, choices=METHOD_CHOICES)
    transaction_id = models.CharField("ID da Transação", max_length=100, blank=True, help_text="ID do Pix ou código da maquininha")

    def __str__(self):
        return f"Pagamento R$ {self.amount} ({self.get_method_display()})"

class Refund(TimeStampedModel):
    """
    Registra estornos totais ou parciais de um pagamento específico.
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField("Valor Estornado", max_digits=10, decimal_places=2)
    reason = models.TextField("Motivo do Estorno")

    def __str__(self):
        return f"Estorno R$ {self.amount} - {self.reason[:30]}..."
