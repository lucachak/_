# ⚡ EletricBike Manager

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Status](https://img.shields.io/badge/Status-Development-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> Um sistema de e-commerce robusto para venda de bicicletas elétricas e kits de conversão, focado em integridade de dados e interface moderna (Glassmorphism).

---

## 📋 Sobre o Projeto

Este projeto é uma plataforma completa de gestão de vendas e estoque. Diferente de e-commerces básicos, este sistema foi arquitetado para lidar com problemas reais de engenharia de software, como **Race Conditions** (Condições de Corrida) no estoque e persistência de dados complexa.

O sistema adota uma arquitetura **Modular**, onde cada domínio do negócio (Vendas, Clientes, Financeiro) vive isolado em sua própria aplicação dentro da pasta `apps/`.

## ✨ Funcionalidades Principais

### 🛒 Vendas e Checkout
- **Carrinho Persistente:** O carrinho é salvo no banco de dados. Se o cliente logar em outro dispositivo, seus itens estarão lá.
- **Controle de Concorrência:** Utilização de `select_for_update()` e `transaction.atomic()` para garantir que dois usuários não comprem o último item do estoque simultaneamente.
- **Cupons de Desconto:** Sistema dinâmico de aplicação de vouchers.

### 🎨 Interface (Front-end)
- **Glassmorphism UI:** Design moderno utilizando transparências, *blur* e componentes flutuantes.
- **Responsividade:** Layout adaptável para mobile e desktop via Bootstrap 5 customizado.

### 📦 Gestão
- **Pedidos:** Fluxo de status (Orçamento → Aprovado → Em Separação → Finalizado).
- **Estoque:** Baixa automática apenas após confirmação de pagamento/aprovação.

---

## 🛠️ Stack Tecnológica

* **Backend:** Python 3, Django Framework
* **Banco de Dados:** SQLite (Dev) / PostgreSQL (Prod - Recomendado)
* **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
* **Templating:** Django Templates (DTL) com filtros `humanize`

---

## 📂 Estrutura do Projeto

O projeto segue o padrão *Modular Monolith*, mantendo a raiz limpa:

```text
├── apps/                  # Núcleo da Aplicação
│   ├── Accounts/          # Gestão de Usuários e Auth
│   ├── Assets/            # Produtos e Estoque
│   ├── Billing/           # Faturamento e Notas
│   ├── Clients/           # Perfis de Clientes
│   ├── Orders/            # Carrinho e Pedidos (Lógica Principal)
│   └── Staff/             # Área Administrativa
|── products               # Imagens
|── media                  # Imagens 
├── Static/                # Arquivos CSS/JS/Imagens globais
├── Templates/             # HTML Base e Componentes
├── manage.py
└── requirements.txt