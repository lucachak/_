from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .models import User, UserProfile

# Inline para ver o perfil dentro do usuário
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil Extra'

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = ('email', 'first_name', 'is_staff', 'is_client_badge')
    ordering = ('email',)
    inlines = [UserProfileInline]

    # Removemos username dos fieldsets padrão pois usamos email
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Sistema', {'fields': ('is_client', 'is_staff_member')}),
    )

    def is_client_badge(self, obj):
        return obj.is_client
    is_client_badge.boolean = True
    is_client_badge.short_description = "Cliente?"
