# coverage run --source nextcloud_async -m pytest
# coverage lcov -o ./lcov.info
pytest --continue-on-collection-errors --cov=nextcloud_async --cov-report lcov:lcov.info tests/