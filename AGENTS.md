# AGENTS.md

This repository is a Python project organized around the `Atoms/` package, with root-level automation in `Makefile` and product documentation in [README.md](README.md) and [Atoms/README.md](Atoms/README.md).

## Project shape

- Root commands live in [Makefile](Makefile) and are the default entry point for setup, validation, and app execution.
- The application code lives under [Atoms/src](Atoms/src).
- The test suite lives under [Atoms/tests](Atoms/tests), including regression checks in [Atoms/tests/regressao](Atoms/tests/regressao).
- Keep architectural boundaries intact: domain logic belongs in `src/models`, web/API concerns in `src/controllers`, UI assets in `src/views`, and shared utilities in `src/utils`.

## Required conventions

- Use imports in the form `src.*` inside the package. Do not introduce `from models...`, `from utils...`, or other non-package-relative imports.
- Preserve the hexagonal architecture and avoid mixing business logic into Flask handlers or views.
- Tests should stay under `Atoms/tests` and should not write to `Atoms/logs/` directly. Prefer `tmp_path` or a temp log directory when an app factory needs a custom location.
- If a bug is confirmed but not immediately fixed, add or extend a regression test under [Atoms/tests/regressao](Atoms/tests/regressao) with `xfail(strict=True)` before implementing the code change.

## Typical commands

Run these from the repository root:

- `make env` — create the virtual environment and install dependencies
- `make quality` — Ruff + Pylint + MyPy
- `make test` — pytest with coverage
- `make test-utils` / `make test-models` / `make test-controllers` — focused test runs
- `make app-web` — run the Flask app
- `make app-cli ARGS="..."` — run CLI commands
- `make ci` — full validation pipeline

## Working expectations

- Prefer the smallest, most targeted change that matches the issue or feature.
- Before making a code change, inspect the relevant module and the closest existing test file.
- Use existing tests as the source of truth; add or adjust tests when behavior changes.
- Keep naming, comments, and docstrings consistent with the existing Portuguese-language project conventions.

## Useful references

- [README.md](README.md)
- [Atoms/README.md](Atoms/README.md)
- [Atoms/pyproject.toml](Atoms/pyproject.toml)
- [Atoms/tests/arquitetura/test_convencao_imports.py](Atoms/tests/arquitetura/test_convencao_imports.py)
- [Atoms/src/views/static/openapi.yaml](Atoms/src/views/static/openapi.yaml)

These files already capture the main project rules and should be treated as the canonical reference when behavior is unclear.
