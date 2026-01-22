from django.views.generic import UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Client
from .forms import ClientProfileForm
from Orders.models import Order
from django.db.models import Sum


class Dashboard(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        client = request.user.client
        orders = Order.objects.filter(client=client)
        
        context = {
            'total_orders': orders.count(),
            'last_order': orders.order_by('-created_at').first(),
            # Soma total gasta (se houver pedidos)
            'total_spent': orders.filter(status__in=['APPROVED', 'SENT', 'DELIVERED']).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            # Atalho para o endereço
            'address': client.address if client.address else "Não cadastrado"
        }
        return render(request, "client/dashboard.html", context)


class Billing(View):

    def get(self, request, *args, **kwargs):
        context={}

        return render(request, "client/billing.html", context)

class ClientSettings(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = "client/settings.html" # Crie este template
    fields = ['address', 'city', 'state', 'zip_code'] # Campos que o cliente pode editar
    success_url = reverse_lazy('client_settings') # Recarrega a página ao salvar

    def get_object(self):
        # Garante que o usuário só edite o PRÓPRIO perfil de cliente
        return self.request.user.client

    def form_valid(self, form):
        messages.success(self.request, "Configurações atualizadas com sucesso!")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientProfileForm
    template_name = 'public/profile.html'
    success_url = reverse_lazy('client_profile')

    def get_object(self):
        # Garante que pega o Cliente do usuário logado
        # Se não existir, cria um vazio agora mesmo
        client, created = Client.objects.get_or_create(user=self.request.user)
        return client

    def form_valid(self, form):
        messages.success(self.request, "Seus dados foram atualizados com sucesso!")
        return super().form_valid(form)