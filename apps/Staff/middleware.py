from django.shortcuts import render
from .models import SiteConfiguration

from django.contrib.auth import logout
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib import messages


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



class OneSessionPerUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Só verifica se o usuário está logado e é Staff/Admin
        if request.user.is_authenticated and request.user.is_staff:
            
            # Pega a chave da sessão atual do navegador
            current_session_key = request.session.session_key
            
            # Pega a chave que salvamos no cache (a "oficial")
            # Se não tiver cache configurado, o Django usa memória local por padrão
            cache_key = f'user_session_{request.user.id}'
            saved_session_key = cache.get(cache_key)

            # Se existir uma chave salva e for DIFERENTE da atual
            if saved_session_key is not None and current_session_key != saved_session_key:
                # Derruba essa sessão antiga
                logout(request)
                messages.warning(request, "Sua conta foi acessada em outro dispositivo. Você foi desconectado.")
                return redirect('login')

        response = self.get_response(request)
        return response