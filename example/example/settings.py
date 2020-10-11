# Minimalistic settings
import os

os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "=================================================="

DEBUG = True

GETPAID_ORDER_MODEL = "orders.Order"
GETPAID_PAYMENT_MODEL = "getpaid_przelewy24.Payment"

GETPAID_BACKEND_SETTINGS = {
    "getpaid_przelewy24": {
        "pos_id": 123252,
        "secret_id": "09f4976bac3f63f3698a6b463a0ac2a7",
        "crc": "3c76241ef55498ae",
        "confirmation_method": "PULL",  # required for local testing
    },
}

PAYWALL_MODE = "PAY"  # PAY for instant paying, LOCK for pre-auth

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django_fsm",
    "getpaid",
    "getpaid_przelewy24",
    "orders",
    "paywall",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ]
        },
    }
]

WSGI_APPLICATION = "example.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True
