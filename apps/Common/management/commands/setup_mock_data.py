import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from faker import Faker
import uuid




# Importação dos Models
from Assets.models import Category, Product, TechnicalSpec, Maintenance
from Clients.models import Client
from Orders.models import Order, OrderItem

User = get_user_model()

class Command(BaseCommand):
    help = 'Gera dados falsos completos para o sistema (Users, Products, Orders, etc.)'

    def handle(self, *args, **kwargs):
        fake = Faker('pt_BR')
        
        self.stdout.write(self.style.WARNING('⚠️  Iniciando limpeza do banco de dados...'))
        
        # 1. Limpeza (Ordem importa para não quebrar ForeignKeys)
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Maintenance.objects.all().delete()
        TechnicalSpec.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Client.objects.all().delete()
        
        # Não deletamos superusers, apenas users de teste criados anteriormente
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('✅ Banco limpo! Iniciando população...'))

        # --- 2. USUÁRIOS & CLIENTES ---
        clients_list = []
        
        # Criar Staff
        staff_user = User.objects.create_user(
            email='staff@eletricbike.com', 
            password='123', 
            first_name='Mecânico', 
            last_name='Chefe',
            is_staff=True
        )
        self.stdout.write(f'👤 Staff criado: {staff_user.email}')

        # Criar 10 Clientes
        for _ in range(10):
            email = fake.unique.email()
            first_name = fake.first_name()
            user = User.objects.create_user(
                email=email,
                password='123',
                first_name=first_name,
                last_name=fake.last_name()
            )
            
            # Perfil do Cliente
            client = Client.objects.create(
                user=user,
                address=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zip_code=fake.postcode(),
                internal_notes=f"Cliente veio por indicação. Gosta de {fake.word()}."
            )
            clients_list.append(client)
        
        self.stdout.write(f'👥 {len(clients_list)} Clientes criados.')

        # --- 3. CATEGORIAS ---
        # Pai
        cat_bikes = Category.objects.create(name='Bikes Elétricas', icon_class='fa-bicycle')
        cat_parts = Category.objects.create(name='Componentes & Peças', icon_class='fa-microchip')
        cat_services = Category.objects.create(name='Oficina', icon_class='fa-tools', is_service=True)

        # Filhas
        cat_mtb = Category.objects.create(name='Mountain Bike', parent=cat_bikes)
        cat_urban = Category.objects.create(name='Urbana', parent=cat_bikes)
        cat_battery = Category.objects.create(name='Baterias', parent=cat_parts)
        cat_motor = Category.objects.create(name='Motores', parent=cat_parts)

        # --- 4. PRODUTOS (Mix Variado) ---
        products_list = []

        # A. BIKES (High Ticket)
        bike_names = ['Thunder', 'Storm', 'CityFlow', 'UrbanX', 'MountainKing']
        for _ in range(8):
            nome = f"{random.choice(bike_names)} {fake.word().upper()}"
            bike = Product.objects.create(
                name=nome,
                sku=f"BK-{str(uuid.uuid4())[:8].upper()}",
                category=random.choice([cat_mtb, cat_urban]),
                product_type='BIKE',
                selling_price=random.randint(4500, 12000),
                cost_price=random.randint(2000, 4000),
                stock_quantity=random.randint(0, 5),
                description=fake.text(),
                short_description="Bike elétrica de alta performance.",
                is_featured=random.choice([True, False]),
                condition='NEW'
            )
            # Specs da Bike
            TechnicalSpec.objects.create(
                product=bike,
                voltage=random.choice([36, 48, 60]),
                wattage=random.choice([350, 500, 750, 1000]),
                max_speed=random.choice([25, 32, 45]),
                range_estimate=f"{random.randint(30, 80)} km",
                weight=random.randint(18, 28),
                material="Alumínio 6061"
            )
            products_list.append(bike)

        # B. PEÇAS (Componentes)
        parts_data = [
            ('Bateria Samsung 48v', cat_battery, 1800, 1200),
            ('Controlador 350w', cat_motor, 250, 100),
            ('Display LCD SW900', cat_parts, 300, 150),
            ('Acelerador de Dedo', cat_parts, 80, 30),
            (' BMS 13s 30a', cat_battery, 120, 50),
        ]
        
        for name, cat, price, cost in parts_data:
            part = Product.objects.create(
                name=name,
                sku=f"PRT-{str(uuid.uuid4())[:8].upper()}",
                category=cat,
                product_type='COMPONENT',
                selling_price=price,
                cost_price=cost,
                stock_quantity=random.randint(10, 50),
                description="Peça de reposição original."
            )
            TechnicalSpec.objects.create(
                product=part,
                voltage=48,
                material="Plástico ABS / Lítio"
            )
            products_list.append(part)

        # C. SERVIÇOS
        services_data = [
            ('Revisão Geral', 150),
            ('Troca de Pneu', 40),
            ('Diagnóstico Elétrico', 120),
            ('Montagem de Kit', 450)
        ]
        
        service_objs = []
        for name, price in services_data:
            svc = Product.objects.create(
                name=name,
                sku=f"SVC-{fake.random_number(digits=3)}",
                category=cat_services,
                product_type='SERVICE',
                selling_price=price,
                stock_quantity=999 # Infinito
            )
            service_objs.append(svc)
            products_list.append(svc)

        self.stdout.write(f'📦 {len(products_list)} Produtos criados.')

        # --- 5. PEDIDOS (ORDERS) ---
        statuses = ['QUOTE', 'APPROVED', 'IN_PROGRESS', 'READY', 'FINISHED']
        
        for _ in range(15):
            client = random.choice(clients_list)
            status = random.choice(statuses)
            
            order = Order.objects.create(
                client=client,
                status=status
            )
            
            # Adicionar itens ao pedido
            total = 0
            for _ in range(random.randint(1, 4)):
                prod = random.choice(products_list)
                qty = random.randint(1, 2)
                price = prod.selling_price or 0
                
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit_price=price,
                    description=prod.name
                )
                total += (price * qty)
            
            # Atualiza total do pedido
            order.total_amount = total
            order.save()

        self.stdout.write('🛒 15 Pedidos gerados.')

        # --- 6. MANUTENÇÃO (SERVICE ORDERS) ---
        # Simula bikes de clientes que estão na oficina
        for _ in range(5):
            # Cria uma bike que pertence ao cliente (não é estoque da loja)
            owner = random.choice(clients_list)
            bike_cliente = Product.objects.create(
                name=f"Bike do {owner.user.first_name}",
                category=cat_mtb,
                product_type='BIKE',
                ownership='CUSTOMER', # Importante
                condition='USED'
            )
            
            Maintenance.objects.create(
                product_item=bike_cliente,
                customer_complaint=random.choice([
                    "Motor falhando na subida", 
                    "Freio fazendo barulho", 
                    "Bateria não carrega", 
                    "Pneu furado"
                ]),
                status=random.choice(['PENDING', 'IN_PROGRESS', 'WAITING_PARTS', 'READY']),
                labor_cost=150.00,
                parts_cost=random.randint(0, 500)
            )

        self.stdout.write(self.style.SUCCESS('✅ SETUP CONCLUÍDO COM SUCESSO!'))
        self.stdout.write('👉 Admin: admin@admin.com (se existir) ou crie um novo.')
        self.stdout.write('👉 Staff: staff@eletricbike.com / senha: 123')
