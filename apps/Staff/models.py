from django.db import models
from Common.models import TimeStampedModel

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.cache import cache

class SiteConfiguration(TimeStampedModel):
    """
    Modelo Singleton para configurações globais do site.
    Só deve existir ID=1.
    """
    site_name = models.CharField("Nome do Site", max_length=100, default="EletricBike")
    contact_email = models.EmailField("Email de Contato", default="contato@eletricbike.com")
    whatsapp_number = models.CharField("WhatsApp", max_length=20, blank=True)
    
    # Configs de Negócio
    maintenance_mode = models.BooleanField("Modo Manutenção", default=False)
    free_shipping_threshold = models.DecimalField("Frete Grátis acima de (R$)", max_digits=10, decimal_places=2, default=500.00)

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações"

    def __str__(self):
        return "Configuração Geral"

    def save(self, *args, **kwargs):
        # Garante que sempre seja o ID 1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj



@receiver(user_logged_in)
def register_user_session(sender, request, user, **kwargs):
    if user.is_staff:
        # Salva o ID da sessão atual no cache com o ID do usuário
        # Ex: user_session_1 = 'x78s6d87as6d8...'
        cache_key = f'user_session_{user.id}'
        cache.set(cache_key, request.session.session_key, timeout=None)