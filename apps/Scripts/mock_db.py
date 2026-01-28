
from decimal import Decimal
from django.utils.text import slugify
from Assets.models import Product, Category, TechnicalSpec

def run_seed():
    print("--- Iniciando Importação de Dados ---")

    # 1. CRIAR CATEGORIAS
    # Usamos get_or_create para não duplicar se rodar 2 vezes
    cat_bikes, _ = Category.objects.get_or_create(name="Bicicletas", defaults={'icon_class': 'fas fa-bicycle'})
    cat_kits, _ = Category.objects.get_or_create(name="Kits de Conversão", defaults={'icon_class': 'fas fa-box-open'})
    
    # Subcategorias de Peças
    cat_pecas, _ = Category.objects.get_or_create(name="Peças & Componentes", defaults={'icon_class': 'fas fa-cogs'})
    
    cat_eletrica, _ = Category.objects.get_or_create(
        name="Elétrica", 
        parent=cat_pecas,
        defaults={'icon_class': 'fas fa-bolt'}
    )
    
    cat_mecanica, _ = Category.objects.get_or_create(
        name="Mecânica", 
        parent=cat_pecas,
        defaults={'icon_class': 'fas fa-wrench'}
    )

    print("✅ Categorias criadas.")

    # 2. LISTA DE PRODUTOS (Dados Reais)
    products_data = [
        # BIKES
        {
            "name": "E-Mountain Bike Hardtail 500W",
            "sku": "EBIKE-MTB-500",
            "category": cat_bikes,
            "type": "BIKE",
            "price": "5890.00",
            "stock": 3,
            "desc": "Bike robusta para trilha leve. Quadro alumínio, suspensão dianteira.",
            "specs": {"wattage": 500, "voltage": 36, "max_speed": 35, "material": "Alumínio 6061"}
        },
        {
            "name": "City Commuter 350W (Urbana)",
            "sku": "EBIKE-CITY-350",
            "category": cat_bikes,
            "type": "BIKE",
            "price": "4200.00",
            "stock": 5,
            "desc": "Ideal para delivery e trabalho. Quadro baixo, bagageiro incluso.",
            "specs": {"wattage": 350, "voltage": 36, "max_speed": 25, "range_estimate": "30-40km"}
        },
        
        # KITS
        {
            "name": "Kit Conversão Completo 1000W",
            "sku": "KIT-1000W-RR",
            "category": cat_kits,
            "type": "KIT",
            "price": "2450.00",
            "stock": 10,
            "desc": "Transforme sua bike comum. Inclui motor cubo traseiro, controlador e manetes.",
            "specs": {"wattage": 1000, "voltage": 48, "max_speed": 55}
        },

        # PEÇAS ELÉTRICAS (COMPONENT)
        {
            "name": "Bateria Lítio 36V 13Ah (Garrafa)",
            "sku": "BAT-36V-13AH",
            "category": cat_eletrica,
            "type": "COMPONENT",
            "price": "1800.00",
            "stock": 8,
            "desc": "Bateria removível tipo garrafa. Células Samsung originais.",
            "specs": {"voltage": 36, "amperage": 13.0, "weight": 3.5, "material": "Li-Ion"}
        },
        {
            "name": "Módulo Controlador 350W/36V",
            "sku": "CTRL-350-36",
            "category": cat_eletrica,
            "type": "COMPONENT",
            "price": "280.00",
            "stock": 15,
            "desc": "Controlador brushless sine-wave. Reposição universal.",
            "specs": {"voltage": 36, "wattage": 350, "dimensions": "10x6x3 cm"}
        },
        {
            "name": "Display LCD SW900",
            "sku": "DISP-SW900",
            "category": cat_eletrica,
            "type": "COMPONENT",
            "price": "350.00",
            "stock": 12,
            "desc": "Painel completo com velocímetro, odômetro e nível de bateria.",
            "specs": {"voltage": 36} # Funciona em 36 ou 48, mas definimos um base
        },
        
        # PEÇAS MECÂNICAS (COMPONENT)
        {
            "name": "Pastilha de Freio Hidráulico (Par)",
            "sku": "PAD-HYD-01",
            "category": cat_mecanica,
            "type": "COMPONENT",
            "price": "45.00",
            "stock": 50,
            "desc": "Composto semi-metálico. Alta durabilidade e baixo ruído.",
            "specs": {"material": "Semi-metálica"}
        },
        {
            "name": "Corrente Reforçada E-Bike 9v",
            "sku": "CHAIN-E9",
            "category": cat_mecanica,
            "type": "COMPONENT",
            "price": "180.00",
            "stock": 20,
            "desc": "Tratamento anti-corrosão e pinos reforçados para torque elétrico.",
            "specs": {"material": "Aço Temperado"}
        },
        {
            "name": "Pneu Anti-Furo 29x2.10",
            "sku": "TIRE-29-AF",
            "category": cat_mecanica,
            "type": "COMPONENT",
            "price": "220.00",
            "stock": 18,
            "desc": "Camada interna de kevlar 5mm. Ideal para uso urbano intenso.",
            "specs": {"dimensions": "29x2.10"}
        }
    ]

    # 3. LOOP DE INSERÇÃO
    for item in products_data:
        # Cria ou Atualiza o Produto Base
        product, created = Product.objects.get_or_create(
            sku=item['sku'],
            defaults={
                'name': item['name'],
                'category': item['category'],
                'product_type': item['type'],
                'selling_price': Decimal(item['price']),
                'stock_quantity': item['stock'],
                'description': item['desc'],
                'ownership': 'SHOP', # É produto de venda
                'is_active': True,
                'condition': 'NEW'
            }
        )
        
        status = "Criado" if created else "Já existia"
        print(f"🚴 {status}: {product.name}")

        # Cria ou Atualiza a Ficha Técnica (Specs)
        if 'specs' in item:
            specs_data = item['specs']
            
            # Tenta pegar a spec existente ou cria uma nova
            spec, spec_created = TechnicalSpec.objects.get_or_create(product=product)
            
            # Atualiza os campos
            updated = False
            for field, value in specs_data.items():
                if getattr(spec, field) != value:
                    setattr(spec, field, value)
                    updated = True
            
            if updated or spec_created:
                spec.save()
                print(f"   └── Specs {'criadas' if spec_created else 'atualizadas'}")

    print("\n🎉 Processo finalizado com sucesso!")

# Executa a função
run_seed()