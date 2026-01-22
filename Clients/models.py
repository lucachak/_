from django.db import models
from django.conf import settings
from Common.models import TimeStampedModel # <--- Ajustado

class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client')
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    
    # Endereço
    address = models.CharField("Endereço", max_length=255, null=True, blank=True)
    number = models.CharField("Número", max_length=10, null=True, blank=True)
    complement = models.CharField("Complemento", max_length=50, null=True, blank=True)
    district = models.CharField("Bairro", max_length=100, null=True, blank=True)
    city = models.CharField("Cidade", max_length=100, null=True, blank=True)
    state = models.CharField("Estado", max_length=2, null=True, blank=True) # UF (SP, RJ...)
    zip_code = models.CharField("CEP", max_length=9, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.cpf}"

    def is_complete(self):
        """Helper para saber se o cadastro está apto para compra"""
        return all([self.cpf, self.phone, self.address, self.city, self.state, self.zip_code])



class ClientContact(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField("Nome", max_length=100)
    phone = models.CharField("Telefone", max_length=20)
    role = models.CharField("Vínculo", max_length=50)

    def __str__(self):
        return f"{self.name} ({self.role})"
