from django import forms
from .models import SiteConfiguration

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = ['site_name', 'contact_email', 'whatsapp_number', 'free_shipping_threshold', 'maintenance_mode']
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control form-control-dark'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control form-control-dark'}),
            'free_shipping_threshold': forms.NumberInput(attrs={'class': 'form-control form-control-dark'}),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }