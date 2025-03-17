coverage run --source nextcloud_async -m pytest tests/unit --block-network
coverage lcov -o ./lcov.info
# pytest --block-network -cov=nextcloud_async --cov-report lcov:lcov.info tests
