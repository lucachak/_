from django.db import models
import uuid

class TimeStampedModel(models.Model):
    """Modelo abstrato: adiciona created_at e updated_at em tudo automaticamente."""
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        abstract = True

class UUIDModel(models.Model):
    """Opcional: Para usar IDs seguros (UUID)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
