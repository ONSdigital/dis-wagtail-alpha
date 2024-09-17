import gunicorn
import gunicorn.glogging


# Tell gunicorn to run our app
wsgi_app = "ons_alpha.wsgi:application"

# Replace gunicorn's 'Server' HTTP header to avoid leaking info to attackers
gunicorn.SERVER = ""

# Restart gunicorn worker processes every 1200-1250 requests
max_requests = 1200
max_requests_jitter = 50

# Log to stdout
accesslog = "-"

# Time out after 25 seconds (notably shorter than Heroku's)
timeout = 25

# Load app pre-fork to save memory and worker startup time
preload_app = True

# Add milliseconds to gunicorn's log messages
gunicorn.glogging.Logger.datefmt = None
del gunicorn.glogging.CONFIG_DEFAULTS["formatters"]["generic"]["datefmt"]
