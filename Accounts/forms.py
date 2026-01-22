from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Formulário para criar conta no site (Registro)"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }

class CustomUserChangeForm(UserChangeForm):
    """Formulário para alterar dados sensíveis no Admin"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_active')

class UserProfileForm(forms.ModelForm):
    """Formulário para o usuário editar Whatsapp e Avatar na área logada"""
    class Meta:
        model = UserProfile
        fields = ['whatsapp', 'avatar', 'cpf']
        widgets = {
            'whatsapp': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '(13) 99999-9999'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': '000.000.000-00'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100'
            })
        }


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica o estilo do seu template aos campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'id': 'email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••',
            'id': 'password'
        })

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name') # Ajuste conforme seu model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
