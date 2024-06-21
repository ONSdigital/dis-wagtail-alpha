from .base import *  # noqa

# Debugging to be enabled locally only
DEBUG = True

# Set the cache backend for development
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# This key to be used locally only.
SECRET_KEY = "foo"

# Enable FE component library
PATTERN_LIBRARY_ENABLED = True

ALLOWED_HOSTS = ["*"]

# Allow requests from the local IPs to see more debug information.
INTERNAL_IPS = ("127.0.0.1", "10.0.2.2")


# This is only to test Wagtail emails.
WAGTAILADMIN_BASE_URL = "http://localhost:8000"


# Display sent emails in the console while developing locally.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Disable password validators when developing locally.
AUTH_PASSWORD_VALIDATORS = []


# Enable Wagtail's style guide in Wagtail's settings menu.
# http://docs.wagtail.io/en/stable/contributing/styleguide.html
INSTALLED_APPS += ["wagtail.contrib.styleguide"]  # noqa


# Disable forcing HTTPS locally since development server supports HTTP only.
SECURE_SSL_REDIRECT = False
# For the same reason the HSTS header should not be sent.
SECURE_HSTS_SECONDS = 0


# Adds Django Debug Toolbar
INSTALLED_APPS.append("debug_toolbar")  # noqa
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa

# Override in `local.py`
SHOW_TOOLBAR = True

DEBUG_TOOLBAR_CONFIG = {
    # The default debug_toolbar_middleware.show_toolbar function checks whether the
    # request IP is in settings.INTERNAL_IPS. In Docker, the request IP can vary, so
    # we set it in settings.local instead.
    "SHOW_TOOLBAR_CALLBACK": lambda x: SHOW_TOOLBAR,
    "SHOW_COLLAPSED": True,
}


# django-crispy-forms
# https://github.com/django-crispy-forms/django-crispy-forms
# -----------------------------------------------------------------------------
CRISPY_FAIL_SILENTLY = False

# Import settings from local.py file if it exists. Please use it to keep
# settings that are not meant to be checked into Git and never check it in.
try:
    from .local import *  # noqa
except ImportError:
    pass
