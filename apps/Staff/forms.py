from django import forms
from .models import SiteConfiguration

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteConfiguration
        fields = ['site_title', 'maintenance_mode', 'contact_email', 'items_per_page']
        widgets = {
            'site_title': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'items_per_page': forms.NumberInput(attrs={'class': 'form-control w-25'}),
        }