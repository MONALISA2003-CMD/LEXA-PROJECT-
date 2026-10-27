# Contributing to LEXA

## Before making a change

1. Read the relevant architecture/operations guide and the affected tests.
2. Keep changes focused; preserve public API contracts and tenant boundaries.
3. Do not alter applied migration filenames, order, or contents without a reviewed forward-only migration strategy.
4. Never commit secrets, production data, authenticated browser state, generated build output, or dependency folders.
5. Add or update tests for behavior changes and security-sensitive paths.

## Local validation

For the web app, use Node.js 24.x and run `npm run typecheck`, `npm test`, and `npm run build` from `apps/web`.

For the API, install `apps/api` with its `dev` extra, set required configuration to disposable local values, and run `python -m compileall -q app` and `python -m pytest tests -q` from `apps/api`.

From the root, run the migration source checks in `migrations/README.md` and `docker compose config --quiet` when the required tools are available. Do not use production services for local tests or replay.

## Pull requests

Explain the user-visible behavior, risks, migration impact, test commands and results, and any environment-dependent validation that remains. A green unit test is not a substitute for authenticated staging acceptance when a change touches multi-tenant writes, accounting, authorization, inventory, or database security.
