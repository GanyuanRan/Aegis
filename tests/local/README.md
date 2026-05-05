# Local Development Tests

This directory is for development-only Aegis test cases.

Files placed here are ignored by git by default and are not part of the public
quality verification surface. Use this directory for:

- machine-specific experiments
- temporary reproduction scripts
- private host or provider checks
- one-off test inputs that should not ship in the open-source repository

Do not make public CI, release checks, README commands, or current authority
docs depend on files in this directory.

If a test becomes reproducible and useful for public quality verification, move
it to the appropriate tracked suite under `tests/`.
