from pathlib import Path
from django.contrib.messages import constants as messages
import os
from decouple import config, Csv
import dj_database_url
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

load_dotenv()


# Environment
ENVIRONMENT = os.getenv("DJANGO_ENV", "development")

# Security Settings
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False") == "True"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')  # ✅ Load the .env file here


# Secret key (replace in production)
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default-key')

# ⚠️ DEBUG OFF for production
#DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')
# Installed apps
INSTALLED_APPS = [
    'import_export',
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app
    'apps.CSP',
    'apps.Major',
    'apps.Minor_1',
    'apps.Minor_2',
    'apps.site_settings',    
    
     # Required for allauth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
]


SITE_ID = 1
# LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"       # Where to go after login
LOGOUT_REDIRECT_URL = "/login" # Where to go after logout
ACCOUNT_LOGOUT_REDIRECT_URL = '/'   # after logout
ACCOUNT_LOGOUT_ON_GET = True

ACCOUNT_ADAPTER = "apps.site_settings.utils.account_adapter.CustomAccountAdapter"


# Session timeout (e.g., 30 mins)
SESSION_COOKIE_AGE = 1800   # 30 * 60 seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# Custom email validation
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True


# settings.py
COMPANY_OPEN_PATHS = ("/company/login", "/company/attendance", "/dept/login", "/dept/logout", "/dept/dashboard",)

CSRF_FAILURE_VIEW = 'apps.site_settings.views.csrf_failure'

YOUR_GOOGLE_CLIENT_ID = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
YOUR_GOOGLE_CLIENT_SECRET = os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "APP": {
            "client_id": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"),
            "secret": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"),
            "key": "",
        }
    }
}

# JAZZMIN_SETTINGS = {
#     "site_title": "Internship Portal Admin",
#     "site_header": "VelTech Internship Portal",
#     "site_brand": "VelTech",
#     "site_logo": "images/LOGO.png",  # Path to your logo in /static/images/
#     "login_logo": "images/VELTECH.png",
#     "welcome_sign": "Welcome to VelTech Internship Admin Panel",
#     "copyright": "VelTech",

# "topmenu_links": [
#     {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"], "icon": "fas fa-tachometer-alt"},

#     # Master Data
#     {"name": "Company List", "model": "internship.company", "icon": "fas fa-building"},
#     {"name": "Student List", "model": "internship.student", "icon": "fas fa-user-graduate"},
#     {"name": "Attendance", "model": "internship.attendance", "icon": "fas fa-calendar-check"},
#     {"name": "Student Reports", "model": "internship.studentreport", "icon": "fas fa-file-alt"},
#     {"name": "Downloadable Files", "model": "internship.downloadable_files", "icon": "fas fa-download"},

#     # Applications
#     {"name": "Internship Applications", "model": "internship.internshipapplication", "icon": "fas fa-briefcase"},

#     # Site Settings & Announcements
#     {"name": "Site Settings", "model": "internship.sitesetting", "icon": "fas fa-cogs"},
#     {"name": "Announcements", "model": "internship.announcement", "icon": "fas fa-bullhorn"},

#     # Feedback / Reports
#     {"name": "User Reports", "model": "internship.userreport", "icon": "fas fa-chart-line"},
# ],


#     # User menu (top right corner)
#     "usermenu_links": [
#         {"name": "Support", "url": "https://veltech.edu.in/support", "new_window": True},
#     ],

#     # Side menu (app ordering)
#     "order_with_respect_to": ["internship", "auth",],

#     # 🎨 ICONS mapping
#     "icons": {
#         "auth": "fas fa-users-cog",
#         "internship.company": "fas fa-building",
#         "internship.student": "fas fa-user-graduate",
#         "internship.attendance": "fas fa-calendar-check",
#         "internship.studentreport": "fas fa-file-alt",
#         "internship.downloadable_files": "fas fa-download",
#         "internship.internshipapplication": "fas fa-briefcase",
#         "internship.sitesetting": "fas fa-cogs",
#         "internship.announcement": "fas fa-bullhorn",
#         "internship.userreport": "fas fa-chart-line",
#     },

#     # Theme and layout options
#     "show_sidebar": True,
#     "show_sidebar_expanded": False,
#     "navigation_expanded": True,
#     "hide_apps": [],
#     "hide_models": [],
#     "changeform_format": "horizontal_tabs",  # or "collapsible", "single"

#     # # UI tweaks
#     "custom_css": "css/admin_custom.css",  # Optional
#     "custom_js": "js/admin_custom.js",     # Optional
#     "use_google_fonts_cdn": True,
#     "changeform_format_overrides": {
#         "auth.user": "collapsible",
#     },

#     "language_chooser": False,
#     # "hide_models": [
#     #     "auth.User",
#     #     "auth.Group",
#     # ]
# }

# JAZZMIN_SETTINGS["show_ui_builder"] = True
# JAZZMIN_UI_TWEAKS = {
#     "navbar_small_text": False,
#     "footer_small_text": False,
#     "body_small_text": False,
#     "brand_small_text": False,
#     "brand_colour": False,
#     "accent": "accent-primary",
#     "navbar": "navbar-gray-dark navbar-dark",
#     "no_navbar_border": True,
#     "navbar_fixed": False,
#     "layout_boxed": False,
#     "footer_fixed": False,
#     "sidebar_fixed": False,
#     "sidebar": "sidebar-light-primary",
#     "sidebar_nav_small_text": False,
#     "sidebar_disable_expand": False,
#     "sidebar_nav_child_indent": False,
#     "sidebar_nav_compact_style": False,
#     "sidebar_nav_legacy_style": False,
#     "sidebar_nav_flat_style": False,
#     "theme": "lux",
#     "dark_mode_theme": None,
#     "button_classes": {
#         "primary": "btn-outline-primary",
#         "secondary": "btn-outline-secondary",
#         "info": "btn-info",
#         "warning": "btn-warning",
#         "danger": "btn-danger",
#         "success": "btn-success"
#     },
#     "actions_sticky_top": False
# }
# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    
    'apps.site_settings.middleware.MaintenanceModeMiddleware',
    'project_management_system.middleware.ForceLogoutOnCompanyPathsMiddleware',   # ✅ correct path
    'project_management_system.middleware.LoginRequiredMiddleware',   # ✅ correct path
    'project_management_system.middleware.DomainRestrictMiddleware',  # ✅ correct path
    'project_management_system.middleware.RoleBasedSessionMiddleware',  # ✅ correct path

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'project_management_system.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Optional global templates
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'project_management_system.wsgi.application'

# Database (SQLite for dev)
DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=not DEBUG  # Disable SSL in local dev only
        )
    }


# Password validators
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

# Timezone and language
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]  # Source static files during development
STATIC_ROOT = BASE_DIR / "staticfiles"  # Collected static files for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # Enable caching and compression

# ✅ Message tags
MESSAGE_TAGS = {
    messages.ERROR: 'alert-danger',
    messages.SUCCESS: 'alert-success',
    messages.INFO: 'alert-info',
    messages.WARNING: 'alert-warning',
}

# ✅ Logging (recommended to debug 500 errors in production)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'ERROR',
    },
}

# Primary key config
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MESSAGE_TAGS = {
    messages.ERROR: 'error',
    messages.SUCCESS: 'success',
    messages.INFO: 'info',
    messages.WARNING: 'warning',
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')


private_key = os.getenv("GOOGLE_PRIVATE_KEY")
if private_key and "\\n" in private_key:
    private_key = private_key.replace("\\n", "\n")


GOOGLE_CONFIG = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": private_key,
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL"),
    "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),
}

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")  # put in .env
# GOOGLE_CREDENTIALS_FILE = os.path.join(BASE_DIR, "google_service.json")



INSTALLED_APPS += ["django_crontab"]
CRONJOBS = [
    ('*/1 * * * *', 'apps.site_settings.utils.google_sheets.sync_sheets_to_db')  # every 5 min
]




CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv("CLOUDINARY_CLOUD_NAME"),
    'API_KEY': os.getenv("CLOUDINARY_API_KEY"),
    'API_SECRET': os.getenv("CLOUDINARY_API_SECRET"),
}

cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
)
