FROM gitpod/workspace-postgres

ARG PYTHON_VERSION=3.12
ARG NODE_VERSION=20

USER root

RUN pyenv install ${PYTHON_VERSION}; exit 0 && python global ${PYTHON_VERSION}
RUN bash -c ". .nvm/nvm.sh && nvm install ${NODE_VERSION} && nvm use ${NODE_VERSION} && nvm alias default ${NODE_VERSION}"
RUN echo "nvm use default &>/dev/null" >> ~/.bashrc.d/51-nvm-fix

ARG POETRY_HOME=${HOME}/.poetry
ARG POETRY_VERSION=1.7.1

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku or Dokku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PATH - Make sure that Poetry is on the PATH
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.12/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.12/using/cmdline.html#cmdoption-u
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
ENV PATH=$PATH:${POETRY_HOME}/bin \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=gitpodtest.settings.dev \
    SECRET_KEY=gitpod \
    RECAPTCHA_PUBLIC_KEY=dummy-key-value \
    RECAPTCHA_PRIVATE_KEY=dummy-key-value \
    DATABASE_URL="postgres://gitpod@localhost/postgres"


# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). This is read by Dokku only. Heroku will ignore this.
EXPOSE 8080

USER gitpod

# Install poetry using pip
RUN pip install --upgrade poetry==${POETRY_VERSION} \
    poetry config virtualenvs.create false
