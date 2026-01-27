from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from Common.models import TimeStampedModel  

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O Email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser, TimeStampedModel):
    username = None 
    email = models.EmailField('Email', unique=True)
    
    # Flags de Sistema
    is_client = models.BooleanField("É Cliente?", default=False)
    is_staff_member = models.BooleanField("É da Equipe?", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cpf = models.CharField('CPF', max_length=14, unique=True, blank=True, null=True)
    whatsapp = models.CharField('WhatsApp', max_length=15)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"Perfil de {self.user.email}"
