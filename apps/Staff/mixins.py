from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class StaffRequiredMixin(UserPassesTestMixin):
    """
    Verifica se o usuário é Staff (Equipe).
    Se não for, manda para o login ou home.
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        # Se estiver logado mas não for staff, manda pra home
        if self.request.user.is_authenticated:
            return redirect('home') # ou 'bike_catalog'
        # Se não estiver logado, manda pro login
        return redirect('login')