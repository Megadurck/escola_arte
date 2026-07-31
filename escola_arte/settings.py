from pathlib import Path
import os
import datetime
from decouple import config
import dj_database_url
# from django.contrib.sites.models import Site

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECRET_KEY
SECRET_KEY = config('SECRET_KEY')

# DEBUG
DEBUG = config('DEBUG', cast=bool)

# ALLOWED_HOSTS
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Application definition

INSTALLED_APPS = [
    # Apps essenciais do Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django.contrib.sites',  # Necessário para o password reset

    # Outros apps que você criou
    'inscricoes',
    'accounts',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'escola_arte.middleware.CustomSessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'escola_arte.middleware.AdminSessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'escola_arte.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'escola_arte' / 'templates',  # Diretório de templates fora dos apps
            BASE_DIR / 'accounts' / 'templates',  # Adiciona o diretório de templates do app 'accounts'

        ],
        'APP_DIRS': True,  # Permite buscar templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'escola_arte.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

default_postgres_url = (
    f"postgresql://{config('PGUSER', default='postgres')}:{config('PGPASSWORD', default='postgres')}"
    f"@{config('PGHOST', default='localhost')}:{config('PGPORT', default='5433')}"
    f"/{config('PGDATABASE', default='escola_arte')}"
)

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL', default=default_postgres_url))
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Em desenvolvimento, coleta em pasta separada para não sujar arquivos rastreados.
if DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_local')
else:
    # Diretório onde os arquivos estáticos serão coletados durante o deploy
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Pastas adicionais de estáticos do projeto (apps já são encontrados automaticamente).
STATICFILES_DIRS = []

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Padrão do Django
    'escola_arte.auth_backends.AdminBackend',  # Seu backend personalizado
]

SESSION_COOKIE_NAME = 'sessionid_user'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=600, cast=int)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# Configurações de e-mail para enviar o link de recuperação de senha
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Segurança (produção)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0 if DEBUG else 31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=not DEBUG, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=not DEBUG, cast=bool)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=not DEBUG, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SAMESITE = config('SESSION_COOKIE_SAMESITE', default='Lax')
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=not DEBUG, cast=bool)
CSRF_COOKIE_SAMESITE = config('CSRF_COOKIE_SAMESITE', default='Lax')
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=not DEBUG, cast=bool)



# Controle de abertura de inscrições (definir INSCRICOES_ABERTAS=True no .env para abrir)
INSCRICOES_ABERTAS = config('INSCRICOES_ABERTAS', default=False, cast=bool)
ANO_LETIVO_ATUAL = config('ANO_LETIVO_ATUAL', default=datetime.date.today().year, cast=int)

# Configurações de autenticação
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = 'inscricoes:pagina_inicial'
LOGOUT_REDIRECT_URL = '/'

# Configurações do WhiteNoise com nomes hashados para evitar cache antigo em produção
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# SITE_ID = 1

# Remova ou comente esta linha
# Site.objects.get_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'localhost'})

