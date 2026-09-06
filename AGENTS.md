# OpenCode Agent Instructions

## Repository Overview
This is a Python project using pyproject.toml for configuration, based on Nextcloud's async client for the Nextcloud API.

## Key Setup Details
- Uses Python 3.10+
- Virtual environment required: `.venv/`
- Use `uv` or `pip install -e .[dev]` to install in development mode

## Development Environment
- Run `pre-commit install` to set up git hooks
- Use the project's provided test runner commands, not generic pytest

## Special Notes
- The client is built primarily using aiohttp and async/await patterns
- The structure includes a `legacy` subdirectory with a client implementation
- The codebase is organized in `src/` directory following Python package structure conventions
- Dependencies are managed via `pyproject.toml`
- Tests can be executed with `pytest` or specific development commands defined in `pyproject.toml`

## Commands to Know
- Run tests: `pytest`
- Code formatting: `ruff check --fix` and `ruff format`
- Linting: `ruff check`
- Type checking: `mypy`

## Key Files/Dirs to Avoid Overwriting
- `src/nextcloud_async/client/legacy/client.py`: Legacy client implementation
- `.pre-commit-config.yaml`: Pre-commit hook configuration
