from django.shortcuts import render
from .models import SiteConfiguration

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Busca a configuração (cacheado pelo Singleton)
        config = SiteConfiguration.get_solo()
        
        # 2. Lista VIP: Caminhos que nunca bloqueiam
        # Importante liberar STATIC e MEDIA para o site não ficar "quebrado" visualmente
        path = request.path_info
        if (path.startswith('/admin/') or 
            path.startswith('/staff/') or 
            path.startswith('/accounts/') or 
            path.startswith('/static/') or 
            path.startswith('/media/')):
            return self.get_response(request)

        # 3. O Bloqueio: Se ON e não for Staff -> 503
        if config.maintenance_mode and not request.user.is_staff:
            return render(request, 'maintenance.html', status=503)

        return self.get_response(request)