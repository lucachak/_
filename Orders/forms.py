from django import forms
from .models import Order, OrderItem
from Assets.models import Service

class QuickOrderForm(forms.ModelForm):
    """Formulário rápido para solicitar serviço"""
    service_type = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label="Qual serviço você precisa?",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg',
            'rows': 3,
            'placeholder': 'Ex: Minha bateria não está carregando...'
        }),
        label="Descreva o problema"
    )

    class Meta:
        model = Order
        fields = [] # Criamos os campos manualmente para simplificar a view
