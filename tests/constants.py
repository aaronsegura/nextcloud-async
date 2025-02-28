import os

NEXTCLOUD_VERSION = os.environ.get('PYTEST_NEXTCLOUD_VERSION', '30')
USER = os.environ.get('PYTEST_NEXTCLOUD_USER', 'admin')
PASSWORD = os.environ.get('PYTEST_NEXTCLOUD_PASSWORD', 'admin')
ENDPOINT = os.environ.get('PYTEST_NEXTCLOUD_ENDPOINT', 'http://localhost:8181')

