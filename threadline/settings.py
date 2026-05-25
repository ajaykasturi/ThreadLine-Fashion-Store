"""
Django settings for the ThreadLine fashion e-commerce project.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: keep the real key out of GitHub in a real deployment.
SECRET_KEY = 'django-insecure-threadline-comp8347-demo-key-change-me'
DEBUG = True
ALLOWED_HOSTS = ['*']  # '*' is fine for a local demo; tighten for production.

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',  # our app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'threadline.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # project-level templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',  # our custom: cart badge on every page
            ],
        },
    },
]

WSGI_APPLICATION = 'threadline.wsgi.application'

# SQLite: zero setup, perfect for a course demo.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Toronto'
USE_I18N = True
USE_TZ = True

# ---- Static files (CSS, JS) ----
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ---- Media files (user + product uploads) ----
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---- Auth redirects ----
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# ============================================================
# EMAIL (for the "forgot password" reset flow)
# ------------------------------------------------------------
# DEFAULT: console backend: the reset link prints in your
# PyCharm terminal. Zero setup, never fails during a demo.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'ThreadLine <noreply@threadline.local>'

# ------------------------------------------------------------
# OPTIONAL: real Gmail SMTP (free). To use it:
#   1. Turn on 2-Step Verification on your Google account
#   2. Google Account > Security > App passwords > generate one
#   3. Comment out the console line above, uncomment the block below,
#      and paste your 16-char app password.
#
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'youraddress@gmail.com'
# EMAIL_HOST_PASSWORD = 'your16charapppassword'
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# ============================================================
