# LEXA

LEXA is a multi-tenant business operations platform with a Next.js web application, a FastAPI service, PostgreSQL persistence, and Redis-compatible infrastructure for cache/queue workloads. The repository contains the application source, SQL migration history and recovery evidence, automated tests, deployment configuration, and operational documentation.

## Architecture

- **Web:** `apps/web` — Next.js, React, TypeScript, shared UI components, same-origin API proxy routes, and browser acceptance tests.
- **API:** `apps/api` — FastAPI application, Pydantic settings/contracts, authentication and workspace authorization, business routes, intelligence endpoints, workers, and API tests.
- **Database:** `migrations` — forward SQL migrations, replay/reconstruction candidates, migration source inventory, ledger snapshots, and migration recovery decisions. Existing migration filenames and ordering are compatibility-sensitive.
- **Infrastructure:** `docker-compose.yml`, `deploy/docker`, `deploy/kubernetes`, and `render.yaml`.
- **Quality gates:** `.github/workflows/ci.yml`, web contract tests, API unit/contract tests, migration source checks, and opt-in end-to-end suites.

## Repository layout

```text
.
├── apps/
│   ├── api/                 # FastAPI application and tests
│   └── web/                 # Next.js application and browser tests
├── deploy/                  # HAProxy and Kubernetes configuration
├── docs/
│   ├── architecture/        # Application and domain design notes
│   ├── decisions/           # Architecture decisions
│   ├── development/         # Developer and source-archive workflow
│   ├── operations/          # Deployment, security, and runbooks
│   ├── product/             # Product, language, and UI standards
│   └── testing/              # Test plans and validation notes
├── fixtures/                # Test fixtures, including type-check fixtures
├── migrations/              # SQL history and reconstruction evidence
├── scripts/                 # Migration checks, local verification, and CI helpers
└── tests/                   # Repository-wide and migration contract tests
```

## Prerequisites

- Node.js **24.x** and npm for the web application (as declared in `apps/web/package.json`).
- Python **3.12 or newer** for the API; CI currently uses Python 3.13.
- Docker Compose for the local multi-service stack.
- PostgreSQL and Redis-compatible services for full local integration or staging tests.

## Web development and checks

```bash
cd apps/web
npm ci --no-audit --no-fund
npm run dev
```

In another shell, run the checks from `apps/web`:

```bash
npm run typecheck
npm test
npm run build
```

The Playwright scripts in `package.json` cover write-enabled acceptance paths. They may require an explicitly configured disposable/staging environment and authenticated storage state. Do not point them at production or commit browser state files.

## API development and checks

Create and activate a virtual environment, then install the project and development dependencies:

```bash
cd apps/api
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Configure the required environment variables using the names in the root `.env.example`; keep real credentials outside source control. For a local-only test run, use values belonging to a disposable local environment and never copy production connection strings or secrets into test commands.

```bash
python -m compileall -q app
python -m pytest tests -q
```

The test suite requires environment settings such as `APP_ENV`, `DATABASE_URL`, `REDIS_URL`, and `JWT_SECRET` to be present for collection. Some tests also require locally available Python packages and/or live services. A successful compile does not prove database, Redis, RLS, or external-service behavior.

## Local services

From the repository root, inspect the rendered Compose configuration before starting services:

```bash
docker compose config --quiet
docker compose up --build
```

The Compose stack defines PostgreSQL, Redis, two API instances, two web instances, an analytics worker, and HAProxy. Local Compose credentials are development defaults only. Replace them before using any non-disposable environment.

## Environment variables

`.env.example` documents variable names and safe placeholders. Important groups include:

- Runtime/configuration: `APP_ENV`, `PUBLIC_APP_URL`, `CORS_ORIGINS`, `LEXA_API_URL`.
- Database/cache: `DATABASE_URL`, `DATABASE_APP_ROLE`, `DATABASE_LOGIN_ROLE`, `REDIS_URL`.
- Authentication: `JWT_SECRET`, `JWT_ISSUER`, `JWT_AUDIENCE`, `ACCESS_TOKEN_MINUTES`, `REFRESH_TOKEN_DAYS`.
- Account recovery/email: `RESEND_API_KEY`, `EMAIL_FROM`, `LEXA_PROXY_SHARED_SECRET`, `PASSWORD_RESET_MINUTES`, `EMAIL_TIMEOUT_SECONDS`.
- AI provider configuration: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`, `CEREBRAS_API_KEY`, `OPENROUTER_API_KEY`, `HUGGINGFACE_API_KEY`, and corresponding `*_MODEL` settings; request/input/output bounds are configured with `LEXA_AI_REQUESTS_PER_MINUTE`, `LEXA_AI_MAX_INPUT_CHARS`, and `LEXA_AI_MAX_OUTPUT_TOKENS`.
- Optional deployment identity metadata: `LEXA_NEON_PROJECT_ID`, `LEXA_NEON_BRANCH_ID`.

Use only server-side environment settings for secrets. Never expose keys through `NEXT_PUBLIC_*`, check in `.env` files, or paste production credentials into issues, logs, or reports. See [provider and credential guidance](docs/operations/provider-credentials.md) and [security policy](SECURITY.md).

## Database migration workflow

Do not run migrations against production as an ad hoc setup step. From the repository root, the non-destructive source and plan checks are:

```bash
python scripts/check_migration_recovery_manifest.py
python scripts/check_migration_sources.py --strict
python scripts/run_clean_migration_replay.py --plan-only
```

A clean semantic replay is a separate gate and may only run against a disposable, empty, loopback PostgreSQL database. `scripts/run_clean_migration_replay.py --apply` enforces repository-specific safety guards; read [the migration policy](migrations/README.md) before use. Never rewrite the names or contents of applied historical migrations to make a local tree appear consistent. Migration `048` contains a source-level correction for a declared variable mismatch; production deployment status was not verified as part of this repository cleanup.

## Deployment

- **Web:** deploy `apps/web` as the Next.js project (Vercel configuration is in `apps/web`).
- **API:** `render.yaml` deploys the FastAPI service from `apps/api`.
- **Database/cache:** use the intended PostgreSQL and Redis-compatible services configured through secret environment variables.
- **Health checks:** `/health` is process liveness; `/ready` checks dependency/schema readiness. Render is configured to use `/health` so a dependency outage does not masquerade as a crashed process. Verify readiness separately before traffic or release decisions.
- **CI:** `.github/workflows/ci.yml` runs API checks, web typecheck/contracts/build, and Compose/HAProxy validation.

For repository-wide replacement by a committed root-level ZIP, install the standalone workflow supplied separately as `.github/workflows/lexa-zip-extract.yml` before uploading `LEXA-cleaned-fixed.zip` (or `LEXA-cleaned.zip`). The extractor is intentionally delivered outside this source ZIP so it can be installed first and preserved across full-tree replacement. It validates the archive, preserves `.git`, commits the cleaned canonical tree to `main`, and explicitly dispatches the canonical CI workflow. GitHub Actions must be allowed to write repository contents and dispatch workflows; branch protections may prohibit direct pushes. The separate `.github/workflows/replace-from-archive.yml` also supports guarded replacement from a GitHub Release asset, with SHA-256, expected branch-head SHA, and explicit `REPLACE_ALL_FILES` confirmation; pull-request mode is its default. See [source archive handling](docs/development/source-archive-handling.md).

## Troubleshooting

- **Web dependency or typecheck issues:** use Node 24.x and install from `apps/web/package-lock.json` with `npm ci`.
- **API test collection fails:** ensure Python dependencies are installed and the required environment variables are set to disposable local values.
- **`/health` succeeds but `/ready` fails:** inspect the API's dependency/schema readiness, database branch identity, configured role/grants, migration status, and Redis availability without exposing connection strings.
- **Migration source check fails:** inspect `migrations/SOURCE_RECOVERY.md`, `migrations/migration_dispositions.json`, and `migrations/reconstructed/README.md`; do not alter production migration history to bypass a check.
- **Browser acceptance tests fail:** confirm the target is a dedicated disposable/staging environment, required migrations are applied there, and authenticated Playwright state was created safely.

## Current validation boundaries

This source archive is a cleaned repository snapshot, not a statement that the live deployment is current or fully accepted. Database migrations have not been applied by this cleanup. Full browser acceptance, live Neon/Redis readiness, external provider calls, and production deployment status require separate environment-specific verification.

## Clean source package

This archive contains the application source, tests, operational scripts, deployment templates, and protected migration history. The GitHub Actions workflows are included under `.github/workflows/` in the repository package; keep workflow files separate if distributing a source-only archive for manual upload. No live production secrets should be committed. Neon PostgreSQL is an external resource and is not modified by packaging.
