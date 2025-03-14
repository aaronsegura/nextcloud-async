# Running Tests

Tests in this package rely on pytest-recording vcr cassettes.  In order to
have a reliable source for recording cassettes, a docker-compose.yml file is
provided along with two environment files.  The enviornment files
(.env_latest and .env_legacy) are configured for the two latest supported
major versions of Nextcloud as of the release of this package.

Latest -> Nextcloud v30

Legacy -> Nextcloud v29

You may run them both concurrently.

    $ docker compose --env-file .env_latest -d up
    ...
    $ docker compose --env-file .env_legacy -d up
    ...
    $ docker container list
    CONTAINER ID   IMAGE           COMMAND                  CREATED        STATUS        PORTS                                     NAMES
    e59cc3e5143e   nextcloud:29    "/entrypoint.sh apac…"   37 hours ago   Up 37 hours   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp   legacy-app-1
    db79a721ebd3   mariadb:10.11   "docker-entrypoint.s…"   37 hours ago   Up 37 hours   3306/tcp                                  legacy-db-1
    6e6d0878095e   nextcloud:30    "/entrypoint.sh apac…"   37 hours ago   Up 37 hours   0.0.0.0:8181->80/tcp, [::]:8181->80/tcp   latest-app-1
    f5213b3f4603   mariadb:10.11   "docker-entrypoint.s…"   37 hours ago   Up 37 hours   3306/tcp                                  latest-db-1

Latest version is available on :8181

Legacy version is available on :8080

Default behavior is to test against the latest cassettes.  In order to test
against legacy cassettes, set PYTEST_NEXTCLOUD_VERSION=29.

If you would rather test against another instance of nextcloud, delete the
existing cassettes at ./tests/cassettes/ and export the appropriate environment
variables before running the first tests:

    PYTEST_NEXTCLOUD_VERSION=yourVersion
    PYTEST_NEXTCLOUD_ENDPOINT=https://yourcloud.com/
    PYTEST_NEXTCLOUD_USER=yourUser
    PYTEST_NEXTCLOUD_PASSWORD=yourPassword

New cassettes are created on first run and written to ./tests/cassettes.
Subsequent test runs will read from the cassettes in order to provide
predicatable results in a timely manner.  They can be removed at any
time and will be recreated on next run.

Test creates a working directory on the instance at `/.nextcloud-async-pytest`
in order to test various functions.  It is removed at the end of the testing
session unless there are errors, in which case it it left behind for your
inspection.
