from django.db import models
from django.db import transaction # Importe aqui em cima para ficar limpo
from Common.models import TimeStampedModel
from Clients.models import Client
from Assets.models import Product 
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.IntegerField( # Renomeei para ficar mais claro
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentagem de desconto (0 a 100)"
    )
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ('QUOTE', 'Orçamento'),
        ('APPROVED', 'Aprovado'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('READY', 'Pronto'),
        ('FINISHED', 'Finalizado'),
        ('CANCELED', 'Cancelado'),
    ]

    # [CORREÇÃO CRÍTICA]: PROTECT impede apagar clientes com dívidas/histórico
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='orders')
    
    # Adicionei o campo de cupom opcional
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUOTE')
    total_amount = models.DecimalField("Valor Total", max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.client}" # Ajustei pois client.user pode falhar se não tiver select_related

    def update_total(self):
        """
        Recalcula total somando itens e aplicando desconto se houver.
        """
        # Soma bruta
        subtotal = sum(item.subtotal for item in self.items.all())
        
        # Aplica desconto do cupom
        if self.coupon and self.coupon.active:
            discount_amount = (subtotal * Decimal(self.coupon.discount_percent)) / 100
            self.total_amount = subtotal - discount_amount
        else:
            self.total_amount = subtotal
            
        self.save()

    def approve_payment(self):
        """
        Aprova o pedido e baixa o estoque atomicamente.
        """
        if self.status == 'APPROVED':
            return 

        with transaction.atomic():
            # Itera sobre os itens para baixar estoque
            for item in self.items.all():
                # Verifica se o produto ainda existe (caso seja nulo)
                if item.product and item.product.product_type != 'SERVICE':
                    # Trava o produto no banco (Lock)
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    
                    if product.stock_quantity >= item.quantity:
                        product.stock_quantity -= item.quantity
                        product.save()
                    else:
                        raise ValueError(f"Estoque insuficiente para: {product.name}")
            
            self.status = 'APPROVED'
            self.save()
            
            # Opcional: Criar registro na timeline aqui automaticamente
            OrderTimeline.objects.create(order=self, status='APPROVED', note="Pagamento aprovado e estoque baixado.")

    def cancel_order(self):
        if self.status == 'CANCELED':
            return

        with transaction.atomic():
            if self.status in ['APPROVED', 'READY', 'IN_PROGRESS']:
                for item in self.items.all():
                    if item.product and item.product.product_type != 'SERVICE':
                        product = Product.objects.select_for_update().get(id=item.product.id)
                        product.stock_quantity += item.quantity
                        product.save()
            
            self.status = 'CANCELED'
            self.save()
            OrderTimeline.objects.create(order=self, status='CANCELED', note="Pedido cancelado e itens estornados.")

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # PROTECT aqui também é recomendado, mas SET_NULL é aceitável se tiver snapshot
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, related_name='order_items')
    
    description = models.CharField("Descrição", max_length=150, blank=True)
    quantity = models.PositiveIntegerField("Quantidade", default=1)
    unit_price = models.DecimalField("Preço Unitário", max_digits=10, decimal_places=2, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Snapshot dos dados do produto
        if self.product:
            if self.unit_price is None:
                self.unit_price = self.product.selling_price or 0
            
            if not self.description:
                prefix = f"[{self.product.sku}] " if hasattr(self.product, 'sku') and self.product.sku else ""
                self.description = f"{prefix}{self.product.name}"
            
        super().save(*args, **kwargs)
        # Opcional: Chamar update_total do pedido pai
        # self.order.update_total() 

    @property
    def subtotal(self):
        if self.unit_price and self.quantity:
            return self.unit_price * self.quantity
        return 0

    def __str__(self):
        return f"{self.quantity}x {self.description}"

# Mantive OrderTimeline igual, está ok.
class OrderTimeline(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField("Nota", max_length=200, blank=True)

    def __str__(self):
        return f"{self.order.id} -> {self.status}"