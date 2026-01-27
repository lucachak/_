from django import forms
from .models import Client

class ClientSettingsForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['address', 'city', 'state', 'zip_code']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': 'Ex: Av. Presidente Kennedy, 1234'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': 'Praia Grande'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': 'SP'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:border-purple-500',
                'placeholder': '11700-000'
            }),
        }
class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['cpf', 'phone', 'zip_code', 'address', 'number', 'complement', 'district', 'city', 'state']
        widgets = {
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UF'}),
        }