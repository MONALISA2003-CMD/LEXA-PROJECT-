# Deployment: web, API, database, and cache

## Topology

- **Web:** `apps/web`, a Next.js application deployed as the Vercel project rooted at `apps/web`.
- **API:** `apps/api`, a FastAPI service deployed by the repository's `render.yaml`.
- **Database:** PostgreSQL (the deployed configuration uses Neon).
- **Cache/queue:** Redis-compatible service configured by `REDIS_URL`.

Do not create a second business database on the API hosting provider when PostgreSQL is the configured source of truth.

## Render API

`render.yaml` currently configures a native Python service with root directory `apps/api`, installs `requirements.txt`, starts `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and uses `/health` as the process liveness check.

- `GET /health` (and compatibility alias `/api/health`) reports process liveness without requiring every dependency to be ready.
- `GET /ready` (and compatibility alias `/api/ready`) reports dependency/schema readiness, including required database identity/schema and Redis checks.

Check `/ready` before treating a deployment as fully ready. Do not change the provider health-check path to `/ready` without consciously deciding how dependency outages should affect process health reporting.

Configure the `sync: false` variables directly in the hosting environment. The code expects appropriate database, cache, JWT, CORS, proxy secret, and—when password reset is enabled—email sender settings. Assign `DATABASE_APP_ROLE=lexa_app` only after the target database has the intended role and grants.

## Vercel web

Create the web project with root directory `apps/web` and use the `apps/web/package-lock.json` lockfile. Use Node.js 24.x, with `npm run build` as the production build command (also represented by the app configuration). Set server-only `LEXA_API_URL` to the intended API HTTPS origin.

The browser should use the same-origin `/api/lexa/*` proxy. Do not configure a public API variable as a fallback for server proxy routing: a Preview deployment should fail closed if its own API origin is missing rather than reading production data. Keep `LEXA_PROXY_SHARED_SECRET` server-side and configure matching strong values only in the environments that need the trusted proxy behavior.

Once the web origin is known, set the exact allowed browser origin(s) in API `CORS_ORIGINS`. Use a comma-separated list only when multiple origins are required.

## Release sequence

1. Review the source diff and allow CI to pass on the exact source commit.
2. Confirm the target database branch/identity, required migration state, database role/grants, and backup/rollback approach.
3. Configure API environment variables through the hosting provider, not Git.
4. Deploy the API and check `/health` and `/ready` separately.
5. Deploy the web app from `apps/web` and set its server-only API origin and proxy secret.
6. Verify allowed origins, same-origin proxy behavior, authentication/workspace scoping, and critical read/write journeys on staging.
7. Run authenticated Playwright acceptance only against an explicitly prepared disposable/staging environment.
8. Treat production database migrations as a separate reviewed operation governed by `migrations/README.md`.

## Secrets and request identity

Never commit production `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `RESEND_API_KEY`, or `LEXA_PROXY_SHARED_SECRET`. Never expose them through `NEXT_PUBLIC_*`. Do not trust caller-supplied forwarded-client-IP headers unless they are accepted from a configured trusted proxy using the repository's secret guard. See [provider credentials](provider-credentials.md) and [security policy](../../SECURITY.md).

## Troubleshooting

- If `/health` fails, investigate process startup/runtime logs and deployment configuration.
- If `/health` succeeds but `/ready` fails, investigate database branch identity, schema/migration readiness, role/grants, and Redis availability without disclosing connection strings.
- If a Preview reaches the wrong API, inspect `LEXA_API_URL` and ensure no public fallback is configured.
- If email recovery is unavailable, confirm server-side email configuration and the trusted public URL; do not place an email key in the browser bundle.
