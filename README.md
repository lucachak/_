# ⚡ EletricBike | Gestão de Oficina & E-commerce

Este projeto é uma plataforma integrada para gestão de serviços de manutenção de bicicletas elétricas e venda de kits de conversão. Desenvolvido com foco em escalabilidade, segurança e uma experiência de usuário moderna.

---

## 🚀 Tecnologias Utilizadas

* **Framework Web:** Django (Python)
* **Interface Administrativa:** Django Unfold (UI moderna e responsiva)
* **Frontend Reativo:** HTMX (Interações assíncronas sem refresh) e Bootstrap 5
* **Pagamentos:** Stripe API (Checkout Sessions e Webhooks)
* **Infraestrutura:** Render (Hospedagem e CI/CD)
* **Banco de Dados:** PostgreSQL (Produção no Render)

---

## 🏗️ Arquitetura do Módulo Billing (Financeiro)

O sistema utiliza uma arquitetura de faturamento resiliente, separando o pedido da transação financeira para permitir maior controle de fluxo de caixa:

* **Invoices:** Geradas automaticamente a partir de um Pedido (`Order`).
* **Payments:** Registram cada transação individual via Stripe ou Pix.
* **Webhook Integration:** O sistema escuta eventos assíncronos do Stripe (`checkout.session.completed`) para garantir a atualização do banco de dados mesmo que o usuário feche a aba do navegador.



---

## 🛠️ Configuração de Desenvolvimento (Arch Linux)

Para rodar o projeto localmente:

1.  **Clonar o repositório:**
    ```bash
    git clone [https://github.com/lucachak/_.git](https://github.com/lucachak/_.git)
    cd _
    ```

2.  **Configurar o ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Variáveis de Ambiente (.env):**
    Crie um arquivo `.env` na raiz (não versionado) com as seguintes chaves:
    ```env
    STRIPE_SK=sk_test_...
    STRIPE_WEBHOOK_SECRET=whsec_...
    DEBUG=True
    ```

4.  **Rodar Migrations e Servidor:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## 🌐 Deploy e Produção

O deploy está configurado no **Render**. Para o funcionamento correto da integração de pagamentos em produção:
* As chaves de API estão configuradas no painel **Environment** do Render.
* A URL do Webhook configurada no Stripe Dashboard é `https://ik4kukb02n.onrender.com/billing/webhook/stripe/`.
* Segurança: O domínio está listado em `CSRF_TRUSTED_ORIGINS` no `settings.py`.

---

## 🔒 Segurança

* **Secret Scanning:** O repositório possui proteção contra push de chaves privadas (Stripe Secret Keys).
* **Git Hygiene:** Arquivos `.env` e pastas de ambiente virtual estão devidamente ignorados via `.gitignore`.
* **Idempotência:** O sistema utiliza o `stripe_checkout_id` para prevenir registros duplicados de um mesmo pagamento.
