# Guidelines for Automated Contributions

This repository is a Python project built around the Caster voice toolkit. Use these instructions when proposing or modifying code.

## Coding Style

- Format all Python code with `yapf` using the configuration in `.style.yapf` which specifies a PEP8 base style and a `column_limit` of 90 characters.
- Lint with `pylint` using the provided `.pylintrc`. Only error level checks are enabled.

## Tests

- Run the unit tests through `python tests/testrunner.py`.
- The CI workflow also runs `pylint -E` on `_caster.py` and the `castervoice` package.
- Ensure tests pass on Python 3.11, as referenced in the GitHub Actions workflow.

## Documentation

- Documentation lives in the `docs/` directory and is built with MkDocs. New documentation pages should be added as Markdown files under `docs/` or its subdirectories.
- For feature documentation, see `docs/readthedocs/meta/GRAMMAR_DOCUMENTATION_TEMPLATE.md` for a template.

## Adding New Rules

- Place new language or application rules inside the `castervoice/rules` directory in the appropriate category.

## Pull Requests

- Follow the PR template in `.github/pull_request_template.md` when submitting changes.
- For significant contributions, open an issue first to discuss your plans with the community.


