import os
import shlex
import subprocess

from invoke import run as local
from invoke.tasks import task

# Process .env file
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f.readlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            var, value = line.strip().split("=", 1)
            os.environ.setdefault(var, value)

FRONTEND = os.getenv("FRONTEND", "docker")

PROJECT_DIR = "/app"
LOCAL_DUMP_DIR = "database_dumps"

LOCAL_MEDIA_DIR = "media"
LOCAL_IMAGES_DIR = LOCAL_MEDIA_DIR + "/original_images"
LOCAL_DATABASE_NAME = PROJECT_NAME = "ons_alpha"
LOCAL_DATABASE_USERNAME = "ons_alpha"


############
# Production
############


def dexec(cmd, service="web"):
    args = shlex.split(
        f"docker compose exec -T {shlex.quote(service)} bash -c {shlex.quote(cmd)}"
    )
    return subprocess.run(args)


@task
def build(c):
    """
    Build the development environment (call this first)
    """
    directories_to_init = [LOCAL_DUMP_DIR, LOCAL_MEDIA_DIR]
    directories_arg = " ".join(directories_to_init)

    group = subprocess.check_output(["id", "-gn"], encoding="utf-8").strip()
    local("mkdir -p " + directories_arg)
    local(f"chown -R $USER:{group} {directories_arg}")
    local("chmod -R 775 " + directories_arg)

    subprocess.run(shlex.split("docker compose pull"))
    subprocess.run(shlex.split("docker compose build"))


@task
def start(c):
    """
    Start the development environment
    """
    if FRONTEND == "local":
        args = "docker compose up -d"
    else:
        args = "docker compose --file docker-compose.yml --file docker/docker-compose-frontend.yml up -d"
    subprocess.run(shlex.split(args))


@task
def stop(c):
    """
    Stop the development environment
    """
    subprocess.run(shlex.split("docker compose stop"))


@task
def restart(c):
    """
    Restart the development environment
    """
    stop(c)
    start(c)


@task
def destroy(c):
    """
    Destroy development environment containers (database will lost!)
    """
    subprocess.run(shlex.split("docker compose down"))


@task
def sh(c, service="web"):
    """
    Run bash in a local container
    """
    subprocess.run(["docker", "compose", "exec", service, "bash"])


@task
def sh_root(c, service="web"):
    """
    Run bash in a local container
    """
    subprocess.run(["docker", "compose", "exec", "--user", "root", service, "bash"])


@task
def psql(c, command=None):
    """
    Connect to the local postgres DB using psql
    """
    cmd_list = [
        "docker",
        "compose",
        "exec",
        "db",
        "psql",
        *["-d", LOCAL_DATABASE_NAME],
        *["-U", LOCAL_DATABASE_USERNAME],
    ]
    if command:
        cmd_list.extend(["-c", command])

    subprocess.run(cmd_list)


@task
def delete_docker_database(c, local_database_name=LOCAL_DATABASE_NAME):
    dexec(
        f"dropdb --if-exists --host db --username={PROJECT_NAME} {LOCAL_DATABASE_NAME}",
        "db",
    )
    dexec(
        f"createdb --host db --username={PROJECT_NAME} {LOCAL_DATABASE_NAME}",
        "db",
    )
    # Create extension schema, for error-free restores from Heroku backups
    # (see https://devcenter.heroku.com/changelog-items/2446)
    psql(c, "CREATE SCHEMA heroku_ext;")


@task(
    help={
        "new_default_site_hostname": "Pass an empty string to skip the default site's hostname replacement"
        " - default is 'localhost:8000'"
    }
)
def import_data(
    c, database_filename: str, new_default_site_hostname: str = "localhost:8000"
):
    """
    Import local data file to the db container.
    """
    # Copy the data file to the db container
    delete_docker_database(c)
    # Import the database file to the db container
    dexec(
        f"pg_restore --clean --no-acl --if-exists --no-owner --host db \
            --username={PROJECT_NAME} -d {LOCAL_DATABASE_NAME} {database_filename}",
        service="db",
    )

    # When pulling data from a heroku environment, the hostname in wagtail > sites is not updated.
    # This means when browsing the site locally with this pulled data you can end up with links to staging, or even
    # the live site.
    # --> let's update the default site hostname values
    if new_default_site_hostname:
        if ":" in new_default_site_hostname:
            hostname, port = new_default_site_hostname.split(":")
        else:
            hostname, port = new_default_site_hostname, "8000"
        assert hostname and port and port.isdigit()
        dexec(
            f"psql -c \"UPDATE wagtailcore_site SET hostname = '{hostname}', port = {port} WHERE is_default_site IS TRUE;\""
        )
        print(f"Default site's hostname was updated to '{hostname}:{port}'.")

    print(
        "Any superuser accounts you previously created locally will have been wiped and will need to be recreated."
    )


def delete_local_renditions(c, local_database_name=LOCAL_DATABASE_NAME):
    psql(c, "DELETE FROM images_rendition;")


#######
# Utils
#######


def make_bold(msg):
    return f"\033[1m{msg}\033[0m"


@task
def dellar_snapshot(c, filename):
    """Snapshot the database, files will be stored in the db container"""
    (
        dexec(
            f"pg_dump -d {LOCAL_DATABASE_NAME} -U {LOCAL_DATABASE_USERNAME} > {filename}.psql",
            service="db",
        ),
    )
    print("Database snapshot created")


@task
def dellar_restore(c, filename):
    """Restore the database from a snapshot in the db container"""
    delete_docker_database(c)

    (
        dexec(
            f"psql -U {LOCAL_DATABASE_USERNAME} -d {LOCAL_DATABASE_NAME} < {filename}.psql",
            service="db",
        ),
    )
    print("Database restored.")


@task
def docker_coverage(c):
    return dexec(
        "coverage erase && coverage run manage.py test \
            --settings=ons_alpha.settings.test && coverage report",
    )


@task
def run_test(c):
    """
    Run python tests in the web container
    """
    subprocess.call(
        [
            "docker",
            "compose",
            "exec",
            "web",
            "python",
            "manage.py",
            "test",
            "--settings=ons_alpha.settings.test",
            "--parallel",
        ]
    )


@task
def migrate(c):
    """
    Run database migrations
    """
    subprocess.run(
        ["docker", "compose", "run", "--rm", "web", "./manage.py", "migrate"]
    )
