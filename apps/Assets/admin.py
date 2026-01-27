from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display
from .models import Category, Product, TechnicalSpec, ProductImage, Maintenance

# --- INLINES ---

class TechnicalSpecInline(StackedInline):
    model = TechnicalSpec
    can_delete = False
    verbose_name_plural = "Especificações Técnicas"
    extra = 1
    max_num = 1
    fieldsets = (
        ('Elétrica', {
            'fields': (('voltage', 'amperage', 'wattage'),),
            'classes': ('tab-panel',),
        }),
        ('Performance & Física', {
            'fields': (('max_speed', 'range_estimate', 'charging_time'), ('weight', 'dimensions', 'material')),
            'classes': ('tab-panel',),
        }),
    )

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"


# --- ADMINS PRINCIPAIS ---

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'parent', 'product_count', 'is_service_badge')
    search_fields = ('name',)
    list_filter = ('is_service',)
    prepopulated_fields = {'slug': ('name',)}

    @display(description="É Serviço?", boolean=True)
    def is_service_badge(self, obj):
        return obj.is_service

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Qtd. Produtos"


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    # ATENÇÃO: list_display define o que aparece na tabela
    list_display = (
        'sku_display', 
        'name', 
        'category', 
        'type_badge', 
        'price_display', 
        'stock_status', 
        'ownership_badge',
        'active_switch'
    )
    list_filter = ('product_type', 'category', 'ownership', 'is_active', 'is_featured')
    search_fields = ('name', 'sku', 'description')
    list_per_page = 20
    list_filter_submit = True 
    inlines = [TechnicalSpecInline, ProductImageInline]
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Identificação', {
            'fields': (('name', 'sku'), ('category', 'product_type'), 'slug'),
        }),
        ('Comercial', {
            'fields': (('cost_price', 'selling_price'), ('stock_quantity', 'min_stock_alert')),
            'classes': ('bg-gray-50',),
        }),
        ('Detalhes', {
            'fields': ('description', 'short_description', 'condition', 'ownership'),
        }),
        ('Configurações', {
            'fields': (('is_active', 'is_featured'), 'main_image'),
        }),
    )


    def sku_display(self, obj):
        return obj.sku or "-"
    sku_display.short_description = "SKU"

    def price_display(self, obj):
        if obj.selling_price:
            return f"R$ {obj.selling_price}"
        return "-"
    price_display.short_description = "Preço Venda"

    @display(
        description="Tipo",
        label={
            'BIKE': 'primary',      
            'COMPONENT': 'info',    
            'ACCESSORY': 'success', 
            'SERVICE': 'warning',   
            'KIT': 'danger',        
        }
    )
    def type_badge(self, obj):
        return obj.product_type

    @display(
        description="Estoque",
        label=lambda x: 'danger' if x <= 2 else 'success'
    )
    def stock_status(self, obj):
        if obj.product_type == 'SERVICE':
            return "N/A"
        return obj.stock_quantity

    @display(
        description="Propriedade",
        label={
            'SHOP': 'success',    
            'CUSTOMER': 'warning', 
        }
    )
    def ownership_badge(self, obj):
        return obj.ownership

    @display(description="Ativo", boolean=True)
    def active_switch(self, obj):
        return obj.is_active


@admin.register(Maintenance)
class MaintenanceAdmin(ModelAdmin):
    list_display = ('id_os', 'product_item', 'customer_info', 'status_badge', 'entry_date', 'total_display')
    list_filter = ('status', 'entry_date')
    search_fields = ('product_item__name', 'customer_complaint', 'id')
    autocomplete_fields = ['product_item']
    
    readonly_fields = ['total_estimate_display']

    def id_os(self, obj):
        return f"OS #{obj.id}"
    id_os.short_description = "Nº"

    def customer_info(self, obj):
        return obj.product_item.name
    customer_info.short_description = "Item / Cliente"

    @display(
        description="Status",
        label={
            'PENDING': 'warning',
            'APPROVED': 'info',
            'IN_PROGRESS': 'primary',
            'WAITING_PARTS': 'danger',
            'READY': 'success',
            'DELIVERED': 'success',
        }
    )
    def status_badge(self, obj):
        return obj.status

    def total_display(self, obj):
        return f"R$ {obj.total_estimate()}"
    total_display.short_description = "Total"

    def total_estimate_display(self, obj):
        total = obj.total_estimate()
        return format_html(
            '<span style="font-size: 1.2em; font-weight: bold; color: #10b981;">R$ {}</span> '
            '<small>(Mão de Obra: {} + Peças: {})</small>',
            total, obj.labor_cost, obj.parts_cost
        )
    total_estimate_display.short_description = "Total Estimado"
