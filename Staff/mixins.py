from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class StaffRequiredMixin(AccessMixin):
    """
    Verifica se o usuário é da equipe (is_staff).
    Se não for, chuta para o login ou home.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_staff:
            # Se logado mas não é staff, manda pra Home
            return redirect('home')
            
        return super().dispatch(request, *args, **kwargs)
