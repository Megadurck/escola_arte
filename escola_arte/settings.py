from pathlib import Path
import os
from dotenv import load_dotenv
from decouple import config
import dj_database_url
# from django.contrib.sites.models import Site

# Carregar variáveis do .env
load_dotenv()

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
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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

DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL'))
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

# Diretório onde os arquivos estáticos serão coletados durante o deploy
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Pastas adicionais onde o Django irá procurar arquivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'inscricoes', 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Padrão do Django
    'escola_arte.auth_backends.AdminBackend',  # Seu backend personalizado
]

SESSION_COOKIE_NAME = 'sessionid_user'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'


# Configurações de e-mail para enviar o link de recuperação de senha
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# settings.py

SESSION_COOKIE_SAMESITE = 'None'  # Necessário para cookies cross-site
SESSION_COOKIE_SECURE = True      # Exige HTTPS
CSRF_COOKIE_SAMESITE = 'None'     # Necessário para CSRF em cross-site
CSRF_COOKIE_SECURE = True         # Exige HTTPS



print(config('DATABASE_URL'))  # Isso deve exibir a URL do banco de dados

# Configurações de autenticação
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inscricoes:pagina_inicial'
LOGOUT_REDIRECT_URL = 'login'

# Configurações do WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# SITE_ID = 1

# Remova ou comente esta linha
# Site.objects.get_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'localhost'})

