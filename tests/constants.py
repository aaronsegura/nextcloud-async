import os

NEXTCLOUD_VERSION = os.environ.get('PYTEST_NEXTCLOUD_VERSION', '30')
USER = os.environ.get('PYTEST_NEXTCLOUD_USER', 'admin')
PASSWORD = os.environ.get('PYTEST_NEXTCLOUD_PASSWORD', 'admin')
ENDPOINT = os.environ.get('PYTEST_NEXTCLOUD_ENDPOINT', 'http://localhost:8181')

# test_files.py
FILE_CONTENTS_ORIG = b'[File Contents]'
FILE_CONTENTS_NEW  = b'[Updated File Contents]'
REMOTE_TEST_BASE_DIR = '/.nextcloud-async-pytest'
REMOTE_TEST_DIR_SRC = f'{REMOTE_TEST_BASE_DIR}/src'
REMOTE_TEST_DIR_DEST = f'{REMOTE_TEST_BASE_DIR}/dest'
REMOTE_TEST_SUBDIRS = f'{REMOTE_TEST_DIR_SRC}/some/sub/dirs'
REMOTE_TEST_FILE_SRC = f'{REMOTE_TEST_DIR_SRC}/Somefile.md'
REMOTE_TEST_FILE_DEST = f'{REMOTE_TEST_DIR_DEST}/Someotherfile.md'