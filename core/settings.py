import os
import sys
import dj_database_url 
from pathlib import Path
from decouple import config
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

SECRET_KEY = config('SECRET_KEY', default='chave-insegura-apenas-para-dev')
DEBUG=True
if config('DEBUG', default=False, cast=bool):
    ALLOWED_HOSTS: list[str] = ["*"]

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

INSTALLED_APPS: list[str] = [

    "unfold",
    "unfold.contrib.filters",  
    "unfold.contrib.forms",  
    "unfold.contrib.inlines",  
    "unfold.contrib.import_export", 
    "unfold.contrib.guardian",  
    "unfold.contrib.simple_history",  
    "unfold.contrib.location_field",
    "unfold.contrib.constance",  

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",    
    
    # Internal Apps
    "core",
    "Home", 
    "Assets", 
    "Billing", 
    "Clients", 
    "Orders",  
    "Staff",
    "Accounts", 
    "Common"
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    

    #internal middleware
    'core.middleware.MaintenanceModeMiddleware',
    'Staff.middleware.MaintenanceModeMiddleware',
    'Staff.middleware.OneSessionPerUserMiddleware',
]

ROOT_URLCONF = "core.urls"

TEMPLATES: list[dict[str, bool | list[Path] | str | dict[str, list[str]]]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR/'Templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS= [BASE_DIR / "Static"]  
STATIC_ROOT: Path = BASE_DIR / "staticfiles"  # new

MEDIA_URL = '/media/'
MEDIA_ROOT: Path = BASE_DIR / "media"

AUTH_USER_MODEL = 'Accounts.User'


UNFOLD= {
    "SITE_TITLE": "E-Bikes Manager",
    "SITE_HEADER": "Oficina Dashboard",
    "SITE_URL": "/",

    # Cores baseadas em um tema "Cyber/Electric" (Roxo Profundo)
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
        },
    },
    
    # Barra Lateral Organizada
    "SIDEBAR": {
        "show_search": True,  # Busca global no menu
        "show_all_applications": False, # Esconde a lista padrão bagunçada
        "navigation": [
            {
                "title": "Gestão",
                "separator": True, # Linha divisória
                "items": [
                    {
                        "title": "Pedidos e Vendas",
                        "icon": "shopping_cart", # Ícones do Material Symbols
                        "link": reverse_lazy("admin:Orders_order_changelist"),
                    },
                    {
                        "title": "Oficina (Serviços)",
                        "icon": "build",
                        "link": reverse_lazy("admin:Assets_maintenance_changelist"), # Atalho direto pra manutenção
                    },
                ],
            },
            {
                "title": "Catálogo",
                "separator": True,
                "items": [
                    {
                        "title": "Produtos/Peças",
                        "icon": "box",
                        "link": reverse_lazy("admin:Assets_product_changelist"),
                    },
                    {
                        "title": "Categorias",
                        "icon": "category",
                        "link": reverse_lazy("admin:Assets_category_changelist"),
                    },
                ],
            },
            {
                "title": "Financeiro",
                "items": [
                    {
                        "title": "Faturas (Invoices)",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:Billing_invoice_changelist"),
                    },
                    {
                        "title": "Pagamentos",
                        "icon": "attach_money",
                        "link": reverse_lazy("admin:Billing_payment_changelist"),
                    },
                ],
            },
            {
                "title": "CRM",
                "items": [
                    {
                        "title": "Clientes",
                        "icon": "group",
                        "link": reverse_lazy("admin:Clients_client_changelist"),
                    },
                    {
                        "title": "Usuários do Sistema",
                        "icon": "admin_panel_settings",
                        "link": reverse_lazy("admin:Accounts_user_changelist"),
                    },
                ],
            },
        ],
    },
}

# Adicione ao final do settings.py

LOGOUT_REDIRECT_URL = 'home' 
LOGIN_REDIRECT_URL = 'client_dashboard' 
CART_SESSION_ID = 'cart'

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
CSRF_TRUSTED_ORIGINS = ['https://ik4kukb02n.onrender.com']

EMAIL_BACKEND = config('EMAIL_BACKEND') 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


