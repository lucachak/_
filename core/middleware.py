from django.shortcuts import render
from django.urls import reverse
from Staff.models import SiteConfiguration

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Busca a configuração (Singleton)
        config = SiteConfiguration.get_solo()
        
        # Caminhos que sempre devem funcionar (Admin, Login, Staff)
        path = request.path_info
        if path.startswith('/admin/') or path.startswith('/staff/') or path.startswith('/accounts/'):
            return self.get_response(request)

        # Se manutenção estiver ATIVA e usuário NÃO for Staff -> Bloqueia
        if config.maintenance_mode and not request.user.is_staff:
            return render(request, 'maintenance.html', status=503)

        return self.get_response(request)