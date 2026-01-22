from django.views import View 
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomLoginForm, CustomUserCreationForm

# --- LOGIN ---
class UserLoginView(LoginView):
    template_name = 'auth/login.html' # Ajuste o caminho se sua pasta for 'auth' ou 'accounts'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home') 

    def form_invalid(self, form):
        messages.error(self.request, "Email ou senha incorretos.")
        return super().form_invalid(form)

# --- REGISTRO ---
class UserRegisterView(CreateView):
    template_name = 'auth/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login') 

    def form_valid(self, form):
        messages.success(self.request, "Conta criada com sucesso! Faça login.")
        return super().form_valid(form)

# --- LOGOUT (Híbrido: GET confirma, POST executa) ---
class UserLogoutView(View):
    template_name = 'auth/logout.html'

    def get(self, request):
        # Se o usuário já não estiver logado, manda pro login direto
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Se estiver logado, mostra a tela "Tem certeza?"
        return render(request, self.template_name)

    def post(self, request):
        # AQUI OCORRE O LOGOUT REAL
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, "Você saiu da sua conta com segurança.")
        return redirect('login')
