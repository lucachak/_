from django import forms
from .models import Product, TechnicalSpec

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'category', 'selling_price', 'cost_price', 
            'stock_quantity', 'min_stock_alert', 'condition', 
            'description', 'main_image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-dark', 'placeholder': 'Ex: E-Bike Trek 500W'}),
            'sku': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-dark'}),
            'condition': forms.Select(attrs={'class': 'form-select form-select-dark'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control form-control-dark', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control form-control-dark', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'min_stock_alert': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-dark', 'rows': 4}),
            'main_image': forms.FileInput(attrs={'class': 'form-control form-control-dark'}),
        }

class TechnicalSpecForm(forms.ModelForm):
    class Meta:
        model = TechnicalSpec
        exclude = ['product'] # O produto é vinculado na View
        widgets = {
            'voltage': forms.NumberInput(attrs={'class': 'form-control form-control-dark', 'placeholder': 'Ex: 36'}),
            'wattage': forms.NumberInput(attrs={'class': 'form-control form-control-dark', 'placeholder': 'Ex: 350'}),
            'amperage': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'max_speed': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'material': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'range_estimate': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'charging_time': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
        }