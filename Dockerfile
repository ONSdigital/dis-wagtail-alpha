# We use Debian images because they are considered more stable than the alpine
# ones becase they use a different C compiler. Debian images also come with
# all useful packages required for image manipulation out of the box. They
# however weight a lot, approx. up to 1.5GiB per built image.
FROM python:3.12-slim as production

ARG POETRY_INSTALL_ARGS="--without=dev"
ARG POETRY_VERSION=1.7.1

# Install dependencies in a virtualenv
ENV VIRTUAL_ENV=/venv

RUN useradd ons_alpha --create-home && mkdir /app $VIRTUAL_ENV && chown -R ons_alpha /app $VIRTUAL_ENV

WORKDIR /app

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku or Dokku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PATH - Make sure that Poetry is on the PATH, along with our venv
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.12/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.12/using/cmdline.html#cmdoption-u
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
#  * PORT - default port used. Please match with EXPOSE so it works on Dokku.
#    Heroku will ignore EXPOSE and only set PORT variable. PORT variable is
#    read/used by Gunicorn.
ENV PATH=$VIRTUAL_ENV/bin:$PATH \
    POETRY_INSTALL_ARGS=${POETRY_INSTALL_ARGS} \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=ons_alpha.settings.production \
    PORT=8000

# Make $BUILD_ENV available at runtime
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}

# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). This is read by Dokku only. Heroku will ignore this.
EXPOSE 8000

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    jq \
    unzip \
    && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Install poetry at the system level
RUN pip install --no-cache poetry==${POETRY_VERSION}

# Don't use the root user as it's an anti-pattern and Heroku does not run
# containers as root either.
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER ons_alpha

# Install your app's Python requirements.
RUN python -m venv $VIRTUAL_ENV
COPY --chown=ons_alpha pyproject.toml poetry.lock ./
RUN pip install --no-cache --upgrade pip && poetry install ${POETRY_INSTALL_ARGS} --no-root && rm -rf $HOME/.cache

# Copy application code.
COPY --chown=ons_alpha . .

# Get the Design System templates
RUN make load-design-system-templates

# Run poetry install again to install our project (so the the ons_alpha package is always importable)
RUN poetry install ${POETRY_INSTALL_ARGS}

# Collect static. This command will move static files from application
# directories and "static_compiled" folder to the main static directory that
# will be served by the WSGI server.
RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Load shortcuts
COPY ./docker/bashrc.sh /home/ons_alpha/.bashrc

# Run the WSGI server. It reads PORT and WEB_CONCURRENCY
# environment variables and the rest is configured in `gunicorn.conf.py`.
CMD gunicorn

# These steps won't be run on production
FROM production as dev

# Swap user, so the following tasks can be run as root
USER root

# Install `psql`, useful for `manage.py dbshell`
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    postgresql-client \
    && apt-get autoremove && rm -rf /var/lib/apt/lists/*

# Restore user
USER ons_alpha

# do nothing forever - exec commands elsewhere
CMD tail -f /dev/null
