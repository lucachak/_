from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model # <--- MUDANÇA 1: Importar isso
from .models import SiteConfiguration

class MaintenanceModeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        
        # 1. Configuração Inicial
        self.config = SiteConfiguration.get_solo()
        self.config.maintenance_mode = False
        self.config.save()

        # 2. Cria usuário COMUM (sem username, apenas email)
        self.client_user = Client()
        self.user = User.objects.create_user(
            email='cliente@teste.com', 
            password='123',
            first_name='Cliente' # Opcional, mas bom para logs
        )
        
        # 3. Cria usuário STAFF (sem username, apenas email)
        self.client_staff = Client()
        self.staff = User.objects.create_user(
            email='admin@teste.com', 
            password='123', 
            is_staff=True,
            first_name='Admin'
        )

    def test_access_when_maintenance_is_off(self):
        """Se manutenção estiver OFF, todos acessam a home."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_block_visitor_when_maintenance_is_on(self):
        """Se manutenção estiver ON, visitante toma 503."""
        # Ativa Manutenção
        self.config.maintenance_mode = True
        self.config.save()

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 503)
        self.assertTemplateUsed(response, 'maintenance.html')

    def test_allow_staff_when_maintenance_is_on(self):
        """Se manutenção estiver ON, Staff acessa normal (200)."""
        # Ativa Manutenção
        self.config.maintenance_mode = True
        self.config.save()

        # Loga como Staff
        self.client_staff.force_login(self.staff) # force_login é mais seguro para testes
        
        response = self.client_staff.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_admin_panel_always_accessible(self):
        """O Painel Admin/Staff nunca pode ser bloqueado."""
        self.config.maintenance_mode = True
        self.config.save()

        # Tenta acessar URL do dashboard
        # Se não estiver logado, vai redirecionar (302) para login. Se logar, 200.
        # O importante é NÃO ser 503.
        response = self.client.get(reverse('staff_dashboard')) 
        self.assertNotEqual(response.status_code, 503)