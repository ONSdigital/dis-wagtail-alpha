# ONS Alpha Wagtail site

## Technical documentation

This project contains technical documentation written in Markdown in the `/docs` folder. This covers:

- continuous integration
- deployment
- git branching
- project conventions

You can view it using `mkdocs` by running:

```bash
poetry run mkdocs serve
```

The documentation will be available at: http://localhost:8001/

# Docker Development Setup

This repository includes `docker-compose` configuration for running the project in local Docker containers,
and a fabfile for provisioning and managing this.

There are a number of other commands to help with development using the fabric script. To see them all, run:

```bash
fab -l
```

## Dependencies

The following are required to run the local environment. The minimum versions specified are confirmed to be working:
if you have older versions already installed they _may_ work, but are not guaranteed to do so.

- [Docker](https://www.docker.com/), version 19.0.0 or up
  - [Docker Desktop for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac) installer
  - [Docker Engine for Linux](https://hub.docker.com/search?q=&type=edition&offering=community&sort=updated_at&order=desc&operating_system=linux) installers
- [Docker Compose](https://docs.docker.com/compose/), version 1.24.0 or up
  - [Install instructions](https://docs.docker.com/compose/install/) (Linux-only: Compose is already installed for Mac users as part of Docker Desktop.)
- [Fabric](https://www.fabfile.org/), version 2.4.0 or up
  - [Install instructions](https://www.fabfile.org/installing.html)
- Python, version 3.6.9 or up

Note that on Mac OS, if you have an older version of fabric installed, you may need to uninstall the old one and then install the new version with pip3:

```bash
pip uninstall fabric
pip3 install fabric
```

You can manage different python versions by setting up `pyenv`: https://realpython.com/intro-to-pyenv/

## Running the local build for the first time

If you are using Docker Desktop, ensure the Resources:File Sharing settings allow the cloned directory to be mounted in the web container (avoiding `mounting` OCI runtime failures at the end of the build step).

Starting a local build can be done by running:

```bash
git clone https://github.com/ONSdigital/dis-wagtail-alpha
cd dis-wagtail-alpha
fab build
fab migrate
fab start
```

This will start the containers in the background, but not Django. To do this, connect to the web container with `fab sh`
and run `honcho start` to start both Django and the scheduler in the foreground.

If you only want to run Django, run `honcho start web` or `./manage.py runserver 0.0.0.0:8000`.

Then, connect to the running container again (`fab sh`) and:

```bash
dj createcachetable
dj createsuperuser
```

The site should be available on the host machine at: http://127.0.0.1:8000/

Upon first starting the container, the static files may not exist, or may be out of date. To resolve this, simply run `make load-design-system-templates`.

## Installing Python packages

Python packages can be installed using `poetry` in the web container:

```
fab sh
poetry add wagtail-guide
```

To reset installed dependencies back to how they are in the `poetry.lock` file:

```
fab sh
poetry install --no-root
```

## Installing system packages

If you wish to install extra packages in your local environment, to aid with debugging:

```bash
fab sh-root
apt-get update
apt-get install <package>  # eg. apt-get install vim
```

Then, exit the terminal and connect again using `fab sh`.

If you run `fab build`, or the container is rebuilt for some other reason, these packages will need re-installing.

If a package is always needed (eg a Python package requires a system dependency), this should be added to the `Dockerfile`.


## Local Development Setup

This project uses `poetry` for dependency management and `make` for common development tasks.

### Pre-requisites

Ensure you have the following installed:

1. **Python**: Version specified in `.python-version`. We recommend using [pyenv](https://github.com/pyenv/pyenv) for
   managing Python versions.
2. **[Poetry](https://python-poetry.org/)**: This is used to manage package dependencies and virtual
   environments.

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/ONSdigital/dis-wagtail-alpha.git
   cd dis-wagtail-alpha
   ```

2. Install dependencies:
   ```sh
   poetry install
   ```


### Linting and Formatting

This project uses `Ruff`, `pylint`, and `black` for linting and formatting Python code and `djhtml` for HTML linting.

- To check linting issues:

  ```sh
  make lint
  ```

- To format the code:

  ```sh
  make format
  ```
