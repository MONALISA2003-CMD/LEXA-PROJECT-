# Security policy

## Reporting a vulnerability

Do not publish exploitable details, credentials, tenant data, or production logs in a public issue. Report suspected vulnerabilities privately to the repository maintainers using the private security reporting facilities available for the hosting repository.

## Credential handling

- Keep `.env`, production URLs with embedded credentials, API keys, private keys, and authenticated browser state out of Git and source ZIPs.
- `.env.example` is a variable-name/template file; use a secret manager or deployment environment for real values.
- Rotate any credential that may have been exposed. Removing a file from a later ZIP does not erase it from Git history or invalidate an issued credential.
- Never expose server secrets through client-prefixed variables such as `NEXT_PUBLIC_*`.

## Application security expectations

Changes must preserve tenant/workspace authorization, server-side access control, row-level security (RLS), input validation, secure session/password-reset behavior, and least-privilege database permissions. Fail closed when security-critical configuration is missing. Do not weaken checks to make tests pass.

## Database and release safety

Use the reviewed migration checks and a disposable empty PostgreSQL database for replay. Do not replay or test write-enabled browser flows against production. Migration filenames and already-applied migration contents are history and compatibility boundaries. Follow the database security and deployment guides before applying a change.
