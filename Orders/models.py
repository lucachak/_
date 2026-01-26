from django.db import models
from Common.models import TimeStampedModel
from Clients.models import Client
from Assets.models import Product 
from django.core.validators import MinValueValidator, MaxValueValidator

class Order(TimeStampedModel):
    STATUS_CHOICES = [
        ('QUOTE', 'Orçamento'),
        ('APPROVED', 'Aprovado'),
        ('IN_PROGRESS', 'Em Andamento'),
        ('READY', 'Pronto'),
        ('FINISHED', 'Finalizado'),
        ('CANCELED', 'Cancelado'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUOTE')
    total_amount = models.DecimalField("Valor Total", max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido #{self.id} - {self.client.user.email}"

    def update_total(self):
        """
        Método auxiliar para recalcular o total do pedido 
        somando todos os itens.
        """
        self.total_amount = sum(item.subtotal for item in self.items.all())
        self.save()

    def approve_payment(self):
        """
        Aprova o pedido e baixa o estoque atomicamente.
        """
        if self.status == 'APPROVED':
            return # Já aprovado, evita duplicidade

        from django.db import transaction
        
        with transaction.atomic():
            # Itera sobre os itens para baixar estoque
            for item in self.items.all():
                if item.product.product_type != 'SERVICE':
                    # Trava o produto no banco (SELECT FOR UPDATE)
                    product = item.product.__class__.objects.select_for_update().get(id=item.product.id)
                    
                    if product.stock_quantity >= item.quantity:
                        product.stock_quantity -= item.quantity
                        product.save()
                    else:
                        raise ValueError(f"Estoque insuficiente para: {product.name}")
            
            self.status = 'APPROVED'
            self.save()

    def cancel_order(self):
        """
        Cancela e devolve itens ao estoque.
        """
        if self.status == 'CANCELED':
            return

        from django.db import transaction
        
        with transaction.atomic():
            if self.status in ['APPROVED', 'READY', 'IN_PROGRESS']:
                for item in self.items.all():
                    if item.product.product_type != 'SERVICE':
                        product = item.product.__class__.objects.select_for_update().get(id=item.product.id)
                        product.stock_quantity += item.quantity
                        product.save()
            
            self.status = 'CANCELED'
            self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    
    description = models.CharField("Descrição", max_length=150, blank=True)
    quantity = models.PositiveIntegerField("Quantidade", default=1)
    unit_price = models.DecimalField("Preço Unitário", max_digits=10, decimal_places=2, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.unit_price is None and self.product:
            self.unit_price = self.product.selling_price or 0
        
        if not self.description and self.product:
            prefix = f"[{self.product.sku}] " if self.product.sku else ""
            self.description = f"{prefix}{self.product.name}"
            
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        if self.unit_price and self.quantity:
            return self.unit_price * self.quantity
        return 0

    def __str__(self):
        return f"{self.quantity}x {self.description}"

class OrderTimeline(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='timeline')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField("Nota", max_length=200, blank=True)

    def __str__(self):
        return f"{self.order.id} -> {self.status} em {self.timestamp.strftime('%d/%m %H:%M')}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentagem de desconto (0 a 100)"
    )
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code