"""
Django Settings for TaskCLI Project
====================================
Configuration for both Web App and CLI interface.
Supports environment variables for production deployment.

Author: TaskCLI Team
"""

import os
from pathlib import Path

# =============================================================================
# BASE CONFIGURATION
# =============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
# In production, set DJANGO_SECRET_KEY environment variable
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    'django-insecure-%$#c0hxnvd&qs8-2l1i$^3rrjhg=pp7-rh%n4pze=_#we0z9jd'
)

# SECURITY WARNING: don't run with debug turned on in production!
# Set DJANGO_DEBUG=True for development
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

# Hosts allowed to serve this application
# Set DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com" in production
ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",") if host.strip()
]

# CSRF trusted origins for form submissions
# Set DJANGO_CSRF_TRUSTED_ORIGINS="https://yourdomain.com" in production
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",") if origin.strip()
]

# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.auth',          # Authentication framework
    'django.contrib.contenttypes',  # Content type framework
    'django.contrib.sessions',      # Session framework
    'django.contrib.staticfiles',   # Static file handling
    'accounts',                     # Our main app (tasks, users)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',       # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session handling
    'django.middleware.common.CommonMiddleware',           # Common utilities
    'django.middleware.csrf.CsrfViewMiddleware',           # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Auth
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # X-Frame-Options
]

# =============================================================================
# URL CONFIGURATION
# =============================================================================

ROOT_URLCONF = 'taskcli.urls'

# =============================================================================
# TEMPLATE CONFIGURATION
# =============================================================================

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / "templates"],  # Custom templates directory
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
        ]
    },
}]

# =============================================================================
# WSGI APPLICATION
# =============================================================================

WSGI_APPLICATION = 'taskcli.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# SQLite database - shared between Web App and CLI
# For production, consider PostgreSQL or MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC FILES CONFIGURATION
# =============================================================================

# URL prefix for static files
STATIC_URL = "/static/"

# Additional directories to search for static files
STATICFILES_DIRS = [BASE_DIR / "static"]

# Directory where collectstatic will gather files for production
STATIC_ROOT = BASE_DIR / "staticfiles"

# =============================================================================
# DEFAULT AUTO FIELD
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
