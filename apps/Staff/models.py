from django.db import models

# Create your models here.
class SiteConfiguration(models.Model):
    # Campos de Configuração
    site_title = models.CharField("Nome do Site", max_length=100, default="EletricBike")
    maintenance_mode = models.BooleanField("Modo Manutenção", default=False)
    contact_email = models.EmailField("Email de Contato", default="contato@eletricbike.com")
    items_per_page = models.IntegerField("Itens por página", default=12)

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configuração do Site"

    def save(self, *args, **kwargs):
        # Garante que o ID seja sempre 1 (Padrão Singleton)
        self.pk = 1
        super(SiteConfiguration, self).save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        # Método auxiliar para pegar a config (ou criar se não existir)
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuração Principal"