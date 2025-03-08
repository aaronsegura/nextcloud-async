import os
from nextcloud_async.version import VERSION

NEXTCLOUD_VERSION = os.environ.get("PYTEST_NEXTCLOUD_VERSION", "30")
USER = os.environ.get("PYTEST_NEXTCLOUD_USER", "admin")
PASSWORD = os.environ.get("PYTEST_NEXTCLOUD_PASSWORD", "admin")
ENDPOINT = os.environ.get("PYTEST_NEXTCLOUD_ENDPOINT", "http://localhost:8181")

REMOTE_TEST_DIR = "/.nextcloud-async-pytest"
USER_AGENT = f"nextcloud-async-pytest/{VERSION}"
REQUEST_HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "connection": "keep-alive",
    "ocs-apirequest": True,
    "user-agent": USER_AGENT,
}
