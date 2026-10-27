# Database migrations and source recovery

## Policy

The migration directory is compatibility-sensitive release infrastructure. Preserve existing migration filenames, historical ordering, original bytes, applied ledger entries, and all source-recovery evidence. Do not rename or rewrite an already-applied migration to make a source archive appear consistent. Use a new forward-only migration for an approved correction, and separate source-recovery equivalence from actual semantic replay validation.

The migration history contains multiple identifiers with the same numeric prefix (including `023` and `029`); always identify a migration by its full filename, never by prefix alone. The reconstructed SQL files are explicitly labeled equivalents, compatibility reconciliations, or replay-only files—not original source bytes. Review `SOURCE_RECOVERY.md`, `migration_dispositions.json`, `source_gaps.json`, `reconstructed_source_manifest.json`, and `reconstructed/README.md` for provenance and decisions.

## Non-destructive checks

Run from the repository root:

```bash
python scripts/check_migration_recovery_manifest.py
python scripts/check_migration_sources.py --strict
python scripts/run_clean_migration_replay.py --plan-only
```

These checks validate source inventory, hashes/dispositions, and the declared replay plan. They do not prove that SQL has executed successfully against a clean PostgreSQL instance or that the migration has been deployed to production.

## Disposable semantic replay

A semantic replay is a separate gate. It must use a disposable, empty, loopback PostgreSQL database and the safeguards enforced by the replay script:

```bash
python scripts/run_clean_migration_replay.py --apply
```

Only after a successful replay should the replay evidence check and strict semantic gate be run using the exact commit and evidence path required by the scripts. Never use Neon production or any remote/shared database for replay. Do not run an apply command from this cleanup report as a shortcut to deployment.

## Key invariants

- Never edit production `schema_migrations` rows to force them to match an uploaded archive.
- Never reorder migrations to fit a handoff report.
- Retain migration disposition and live-ledger snapshot files as provenance evidence.
- Keep the QA-only/replay-only status of reconstructed migration files explicit; require a separate reviewed adoption decision before production inclusion.
- Verify row-level security, grants, function ownership/execution rights, tenant isolation, and application compatibility as part of release acceptance.
- Do not claim an applied migration is production-deployed based solely on a local source file or successful source inventory check.

## Source check in migration 048

The cleanup corrected `048_phase7_approval_limits_reversals_accounting.sql` to use its declared `a_cash` variable consistently in the supplier-payment journal function; the original code referenced undefined `v_cash` in that block. A repository contract test checks the declaration and uses and prevents the undefined spelling from returning. This source correction was not applied to a database, and the deployed production migration state was not re-verified here.

## Inventory intelligence and reporting

Migration `036_phase6_inventory_intelligence.sql` establishes per-tenant, per-location, per-variant replenishment policy structures with row-level security and least-privilege grants. The advisory API derives replenishment metrics from eligible completed sales/returns and availability adjustments. Treat the result as advisory only; verify behavior from current source and tests rather than relying on stale phase-specific implementation reports.

## Production migration release gate

Before production application, require: reviewed diff; backup and recovery plan; disposable clean semantic replay; security and tenant-isolation evidence; application compatibility checks; reviewed rollout/rollback procedure; and explicit release approval. A production database was not connected to or modified by this cleanup task.
