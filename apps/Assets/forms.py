from django import forms
from .models import Product, TechnicalSpec, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'product_type', 
            'ownership', 'condition', 'description', 
            'cost_price', 'selling_price', 'stock_quantity', 
            'min_stock_alert', 'is_active', 'is_featured', 'main_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica estilo Bootstrap em todos os campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
        # Checkboxes precisam de classe diferente
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_featured'].widget.attrs.update({'class': 'form-check-input'})

class TechnicalSpecForm(forms.ModelForm):
    class Meta:
        model = TechnicalSpec
        fields = [
            'voltage', 'amperage', 'wattage', 
            'weight', 'dimensions', 'material', 
            'max_speed', 'range_estimate', 'charging_time'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            # Importante: Deixar os campos não obrigatórios no form, 
            # pois nem todo produto tem spec técnica
            self.fields[field].required = False
