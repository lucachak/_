from django.shortcuts import render
from django.views import View


# Create your views here.
class Home(View):
    def get(self, request):
        context = {}

        return render(request, "public/home.html", context)

class About(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'public/about.html', context)

class Pricing(View):
    def get(self, request, *args, **kwargs):
        context = {}

        return render(request, "public/pricing.html", context)
class Services(View):
    def get(self, request, *args, **kwargs):

        context = {}
        return render(request, "public/services.html", context)

class Search(View):

    def get(self, request, *args, **kwargs):
        context = {}

        return render(request, "")

# Para mostrar contador de carrinho e notificações
def navbar_context(request):
    if request.user.is_authenticated:
        return {
            'cart_count': request.user.cart.items.count(),
            'notifications_count': request.user.notifications.unread().count(),
            'notifications': request.user.notifications.all()[:5]
        }
    return {}
