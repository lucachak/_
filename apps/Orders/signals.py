from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(pre_save, sender=Order)
def order_status_change_notification(sender, instance, **kwargs):
    # Se o pedido ainda não tem ID (está sendo criado agora), ignoramos aqui
    if not instance.pk:
        return
    
    try:
        # Buscamos como o pedido estava ANTES de ser salvo
        old_order = Order.objects.get(pk=instance.pk)
        
        # Se o status mudou (ex: de PENDING para APPROVED)
        if old_order.status != instance.status:
            
            subject = f"Atualização do Pedido #{instance.id} - EletricBike"
            
            # Mensagem personalizada para cada status
            status_msg = ""
            if instance.status == 'APPROVED':
                status_msg = "Seu pagamento foi aprovado! Estamos preparando seu envio."
            elif instance.status == 'SENT':
                status_msg = "Sua bike saiu para entrega! Em breve chegará até você."
            elif instance.status == 'DELIVERED':
                status_msg = "Pedido entregue. Obrigado por escolher a EletricBike!"
            elif instance.status == 'CANCELED':
                status_msg = "Seu pedido foi cancelado. Caso tenha dúvidas, entre em contato."
            else:
                status_msg = f"Novo status: {instance.get_status_display()}"

            message = f"""Olá, {instance.client.user.first_name}!
            
Temos novidades sobre sua compra.
{status_msg}

Acesse seu painel para ver mais detalhes:
http://127.0.0.1:8000/clients/dashboard/
            """
            
            # Envia o e-mail (em dev, vai aparecer no terminal)
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.client.user.email],
                fail_silently=False
            )
            print(f"📧 E-mail de status disparado para {instance.client.user.email}")

    except Order.DoesNotExist:
        pass