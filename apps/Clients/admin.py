from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Client, ClientContact

class ClientContactInline(TabularInline):
    model = ClientContact
    extra = 0

@admin.register(Client)
class ClientAdmin(ModelAdmin):
    list_display = ('user_email', 'city', 'whatsapp_link')
    search_fields = ('user__email', 'address')
    inlines = [ClientContactInline]

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

    def whatsapp_link(self, obj):
        # Futuramente você pode colocar um link clicável pro WebWhatsapp aqui
        if hasattr(obj.user, 'profile'):
            return obj.user.profile.whatsapp
        return "-"
    whatsapp_link.short_description = "WhatsApp"
