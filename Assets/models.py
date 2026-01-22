from django.db import models
from django.utils.text import slugify
from Common.models import TimeStampedModel

# --- 1. CATEGORIAS HIERÁRQUICAS ---
class Category(TimeStampedModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True, help_text="Usado na URL (ex: /pecas/eletrica)")
    # Permite criar subcategorias (Ex: Componentes > Conectores)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    icon_class = models.CharField(max_length=50, blank=True, help_text="Classe do ícone (ex: fas fa-bolt)")
    is_service = models.BooleanField(default=False, help_text="Categoria exclusiva para mão de obra?")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

# --- 2. O PRODUTO (NÚCLEO) ---
class Product(TimeStampedModel):
    """
    Tabela Mestra. Tudo que entra na loja ou ordem de serviço é um Product.
    """
    TYPE_CHOICES = [
        ('BIKE', 'Bicicleta Elétrica'),     # Tem quadro, motor, bateria
        ('COMPONENT', 'Peça/Componente'),   # Plugs, Células, Controladores
        ('ACCESSORY', 'Acessório'),         # Capacetes, Trancas
        ('SERVICE', 'Serviço/Mão de Obra'), # Diagnóstico, Montagem
        ('KIT', 'Kit de Conversão'),        # Combo Motor + Bateria
    ]

    OWNERSHIP_CHOICES = [
        ('SHOP', 'Estoque da Loja (Venda)'),
        ('CUSTOMER', 'Pertence ao Cliente (Manutenção)'),
    ]

    CONDITION_CHOICES = [
        ('NEW', 'Novo'),
        ('USED', 'Seminovo/Usado'),
        ('OPEN_BOX', 'Open Box'),
        ('REFURBISHED', 'Recondicionado'),
    ]

    # Identificação
    name = models.CharField("Nome", max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField("SKU/Código", max_length=50, unique=True, blank=True, null=True, help_text="Código de barras ou interno")
    
    # Classificação
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    product_type = models.CharField("Tipo", max_length=20, choices=TYPE_CHOICES, default='COMPONENT')
    ownership = models.CharField("Propriedade", max_length=10, choices=OWNERSHIP_CHOICES, default='SHOP')
    condition = models.CharField("Condição", max_length=20, choices=CONDITION_CHOICES, default='NEW')
    
    # Comercial
    description = models.TextField("Descrição Detalhada", blank=True)
    short_description = models.CharField("Resumo", max_length=200, blank=True, help_text="Para exibição em cards")
    
    cost_price = models.DecimalField("Preço de Custo", max_digits=10, decimal_places=2, null=True, blank=True)
    selling_price = models.DecimalField("Preço de Venda", max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Estoque
    stock_quantity = models.IntegerField("Estoque Atual", default=0)
    min_stock_alert = models.IntegerField("Alerta Mínimo", default=2)
    
    # Visibilidade
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField("Destaque na Home", default=False)

    # Imagem Principal (Thumb)
    main_image = models.ImageField("Imagem Capa", upload_to='products/main/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # 1. Cria o slug base a partir do nome
            base_slug = slugify(self.name)
            
            # 2. Se tiver SKU, incorpora ele para tentar ser único logo de cara
            if self.sku:
                slug_candidate = slugify(f"{base_slug}-{self.sku}")
            else:
                slug_candidate = base_slug

            # 3. VERIFICAÇÃO DE DUPLICIDADE (O segredo está aqui)
            # Enquanto existir um produto com esse slug (e não for este mesmo produto),
            # adicionamos um contador ou hash para tornar único.
            original_candidate = slug_candidate
            counter = 1
            
            # Loop de segurança
            while Product.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{original_candidate}-{counter}"
                counter += 1
            
            self.slug = slug_candidate

        super().save(*args, **kwargs)

    def __str__(self):
        prefix = "[CLI]" if self.ownership == 'CUSTOMER' else "[LOJA]"
        return f"{prefix} {self.name} ({self.sku or 'S/N'})"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


# --- 3. DADOS TÉCNICOS (SATÉLITE) ---
class TechnicalSpec(models.Model):
    """
    Armazena dados de engenharia. 
    Usado para: Bikes, Baterias, Controladores, Plugs.
    Não usado para: Serviços, Acessórios simples.
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='specs')
    
    # Elétrica (Crucial para seu negócio)
    voltage = models.DecimalField("Voltagem (V)", max_digits=5, decimal_places=1, null=True, blank=True, help_text="Ex: 36, 48, 52, 60, 72")
    amperage = models.DecimalField("Amperagem/Capacidade (Ah)", max_digits=6, decimal_places=2, null=True, blank=True)
    wattage = models.IntegerField("Potência (W)", null=True, blank=True, help_text="Potência nominal do motor ou pico")
    
    # Física
    weight = models.DecimalField("Peso (kg)", max_digits=6, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField("Dimensões", max_length=100, blank=True, help_text="Ex: 10x5x2 cm ou Aro 29")
    material = models.CharField("Material", max_length=50, blank=True, help_text="Ex: Alumínio 6061, Nylon, Li-Ion")
    
    # Performance (Bikes)
    max_speed = models.IntegerField("Velocidade Máx (km/h)", null=True, blank=True)
    range_estimate = models.CharField("Autonomia Estimada", max_length=50, blank=True)
    charging_time = models.CharField("Tempo de Recarga", max_length=50, blank=True)

    class Meta:
        verbose_name = "Especificação Técnica"

    def __str__(self):
        return f"Specs de {self.product.name}"


# --- 4. GALERIA DE IMAGENS ---
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


# --- 5. ORDEM DE SERVIÇO / MANUTENÇÃO ---
class Maintenance(TimeStampedModel):
    """
    Representa uma OS (Ordem de Serviço).
    Vincula-se a um produto que PERTENCE AO CLIENTE (ownership='CUSTOMER').
    """
    STATUS_CHOICES = [
        ('PENDING', 'Aguardando Orçamento'),
        ('APPROVED', 'Aprovado'),
        ('IN_PROGRESS', 'Em Execução'),
        ('WAITING_PARTS', 'Aguardando Peças'),
        ('READY', 'Pronto para Retirada'),
        ('DELIVERED', 'Entregue/Finalizado'),
    ]

    # O objeto do conserto (Ex: A Bike Trek do João)
    product_item = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='maintenances',
        limit_choices_to={'ownership': 'CUSTOMER'} # Trava para não fazer manutenção em estoque novo
    )
    
    # Detalhes
    customer_complaint = models.TextField("Reclamação/Problema")
    technical_report = models.TextField("Laudo Técnico", blank=True)
    mechanic_notes = models.TextField("Notas Internas", blank=True)
    
    # Prazos e Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    entry_date = models.DateField("Data Entrada", auto_now_add=True)
    estimated_delivery = models.DateField("Previsão Entrega", null=True, blank=True)
    
    # Financeiro Rápido (O detalhe fino fica no app Orders)
    labor_cost = models.DecimalField("Custo Mão de Obra", max_digits=10, decimal_places=2, default=0)
    parts_cost = models.DecimalField("Custo Peças", max_digits=10, decimal_places=2, default=0)
    
    def total_estimate(self):
        return self.labor_cost + self.parts_cost

    def __str__(self):
        return f"OS #{self.id} - {self.product_item.name}"
