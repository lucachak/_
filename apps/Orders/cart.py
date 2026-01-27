from decimal import Decimal
from django.conf import settings
from Assets.models import Product
from .models import Coupon 


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Recupera o cupom da sessão (se existir)
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, update_quantity=False):
            """
            Adiciona um produto ao carrinho com verificação de estoque.
            """
            product_id = str(product.id)
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': 0, 'price': str(product.selling_price)}
            
            # 1. Calcula a quantidade final desejada
            current_qty_in_cart = self.cart[product_id]['quantity']
            
            if update_quantity:
                desired_qty = quantity
            else:
                desired_qty = current_qty_in_cart + quantity

            # 2. VALIDAÇÃO DE ESTOQUE (A melhoria robusta)
            # Se a quantidade desejada for maior que o estoque real, lançamos erro ou limitamos.
            if desired_qty > product.stock_quantity:
                # Opção A: Lança erro (vamos tratar na view)
                # Opção B: Trava no máximo disponível (vamos usar esta, é mais amigável)
                self.cart[product_id]['quantity'] = product.stock_quantity
                limit_reached = True # Flag para avisar o usuário
            else:
                self.cart[product_id]['quantity'] = desired_qty
                limit_reached = False
                
            self.save()
            return limit_reached # Retorna True se o estoque limitou a adição

    def remove(self, product):
        """
        Remove um produto do carrinho.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Itera sobre os itens do carrinho e busca os produtos no banco de dados.
        """
        product_ids = self.cart.keys()
        # Busca os produtos reais no banco
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Conta quantos itens tem no carrinho.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove o carrinho da sessão
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        # Marca a sessão como "modificada" para garantir que o Django salve
        self.session.modified = True

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                return None
        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100)) * self.get_total_price()
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()