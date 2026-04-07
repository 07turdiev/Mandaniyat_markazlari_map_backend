from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-4#j5e=q&n99a-#p))a9d&!@)ypol9smqms-q448x4&%91%4gkc'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'centers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'centers.middleware.LanguageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

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

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Swagger / OpenAPI
SPECTACULAR_SETTINGS = {
    'TITLE': 'Madaniyat markazlari API',
    'DESCRIPTION': "O'zbekiston Respublikasi madaniyat markazlari interaktiv xaritasi API",
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'TAGS': [
        {'name': 'regions', 'description': 'Viloyatlar'},
        {'name': 'districts', 'description': 'Tumanlar'},
        {'name': 'mahallas', 'description': 'Mahallalar'},
        {'name': 'centers', 'description': 'Madaniyat markazlari'},
        {'name': 'map', 'description': 'Xarita ma\'lumotlari'},
        {'name': 'statistics', 'description': 'Statistika'},
    ],
    'COMPONENT_SPLIT_REQUEST': True,
}

# Jazzmin
JAZZMIN_SETTINGS = {
    'site_title': 'Madaniyat markazlari',
    'site_header': 'Madaniyat markazlari boshqaruv paneli',
    'site_brand': 'Madaniyat',
    'welcome_sign': 'Madaniyat markazlari boshqaruv tizimiga xush kelibsiz',
    'copyright': "O'zbekiston Respublikasi Madaniyat vazirligi",
    'search_model': ['centers.CulturalCenter'],
    'topmenu_links': [
        {'name': 'Bosh sahifa', 'url': 'admin:index', 'permissions': ['auth.view_user']},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'centers.Region': 'fas fa-map',
        'centers.District': 'fas fa-map-marker-alt',
        'centers.CulturalCenter': 'fas fa-landmark',
        'centers.ActivityType': 'fas fa-tags',
    },
    'order_with_respect_to': [
        'centers.CulturalCenter',
        'centers.Mahalla',
        'centers.District',
        'centers.Region',
        'centers.ActivityType',
        'auth',
    ],
    'default_icon_parents': 'fas fa-folder',
    'default_icon_children': 'fas fa-circle',
    'use_google_fonts_cdn': True,
    'show_ui_builder': False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-primary',
    'accent': 'accent-primary',
    'navbar': 'navbar-dark navbar-primary',
    'no_navbar_border': False,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-primary',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': False,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'dark_mode_theme': None,
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}
