# GitHub Actions failure analysis and recovery

**Repository:** `MONALISA2003-CMD/LEXA-`  
**Run inspected:** [40462755388](https://github.com/MONALISA2003-CMD/LEXA-/actions/runs/40462755388)  
**Commit:** `62229405378fc6213b847a68d2595e0211d5928d` — `Delete .github/workflows/lexa-zip-extract.yml`  
**Inspection date:** 2026-10-27

## What the linked run actually did

This run was **LEXA Main Build CI**, not a ZIP-extraction run. Its head commit deleted `.github/workflows/lexa-zip-extract.yml`, so the run had no extractor job and could not apply the cleaned archive. The run only reported the normal three CI jobs.

## Current `main` state confirmed after the run

The latest `main` commit observed during this inspection is [`7e16cbf5ecfc15edc107be7043e25f8e2dc46a8e`](https://github.com/MONALISA2003-CMD/LEXA-/commit/7e16cbf5ecfc15edc107be7043e25f8e2dc46a8e), titled `Add files via upload`. Its GitHub commit diff lists exactly one changed path: a newly added repository-root `LEXA-cleaned.zip`. It does not change the application source. A ZIP committed as a normal file is inert unless an active workflow is configured to process that path; the extractor workflow had already been deleted. The active CI path filters also do not include a root ZIP, so that upload itself does not run the build workflow. This explains why the repository source did not change after the archive upload.

- API unit and contract tests: **passed**.
- TypeScript typecheck: **passed**.
- Docker Compose and HAProxy configuration: **passed**.
- Frontend contract tests: **failed**; the production frontend build was skipped because the test step failed.

The failing contract was `apps/web/tests/brand-visibility-live-brand-visibility.test.mjs`, “desktop sidebar and authentication use the full master artwork.” It searched for the *last* `.app-sidebar .app-brand { ... }` rule and expected that rule itself to contain `background-image`. The last occurrence in the checked-in CSS was only a responsive height override (`height: 82px` and `min-height: 82px`). The master artwork declaration exists in the base CSS rule and continues to cascade into the responsive override, so the test was checking the wrong CSS block rather than proving the logo was absent.

The test helper has been corrected to scan matching rules from newest to oldest until it finds the selector rule containing the required declaration. The logo assets and CSS implementation are retained.

## Why the previous cleaned ZIP could not be applied by the guarded replacement workflow

The existing `.github/workflows/replace-from-archive.yml` calls `scripts/replace_from_archive.py`, whose required-root-path validation expects all of the following:

- `README.md`
- `apps/web/package.json`
- `apps/api/app/main.py`
- `migrations/README.md`
- `.github/workflows/ci.yml`
- `.github/workflows/replace-from-archive.yml`

The earlier cleaned ZIP contained `.github/workflows/lexa-ci.yml` instead of `.github/workflows/ci.yml`. That filename mismatch is sufficient to make the replacement validator reject it before any file is replaced. The corrected ZIP now uses `.github/workflows/ci.yml`, and its CI path filters and repository-contract references have been updated consistently. This is a real compatibility fix, not a relaxation of validation.

## Correct way to apply this archive with the separate extractor

The standalone workflow is delivered as a separate file, **not inside the source ZIP**. This is intentional: the workflow must exist in the repository before the upload event and must be preserved while the full source tree is replaced.

1. Upload the separate `lexa-zip-extract.yml` file into `.github/workflows/lexa-zip-extract.yml` and commit that workflow file first.
2. Check repository **Settings → Actions → General → Workflow permissions**. The workflow declares `contents: write` and `actions: write`; if repository policy restricts these permissions or branch protection prohibits direct pushes, GitHub will reject the source commit and the run will report that explicitly.
3. Upload the complete `LEXA-cleaned-fixed.zip` (or rename it to `LEXA-cleaned.zip`) as a file at the repository root. The ZIP commit triggers the extractor.
4. The extractor checks the exact triggering commit, validates the ZIP checksum and canonical required paths through `scripts/replace_from_archive.py`, rejects unsafe or duplicate ZIP paths, replaces the entire source tree while preserving `.git`, and restores the separately installed extractor workflow.
5. The workflow creates a commit with `[lexa-extractor]` in its message, pushes without force, and explicitly dispatches `.github/workflows/ci.yml`. Explicit dispatch is required because commits made with `GITHUB_TOKEN` do not normally trigger another push workflow.
6. Confirm the extractor run reports a source commit, then open **Actions → LEXA Main Build CI** and verify the run triggered by `workflow_dispatch`. The source is not considered successfully updated until that CI run is green.

The guarded `.github/workflows/replace-from-archive.yml` remains a separate alternative for users who prefer a GitHub Release asset, SHA-256 input, expected branch-head SHA, and explicit `REPLACE_ALL_FILES` confirmation. Do not upload the ZIP merely as a normal file and assume the main CI workflow will extract it; main CI only validates the source tree.

## Limitations

The linked run is the CI run above; it does not expose a log for a separate failed extraction run. The analysis distinguishes the actual logged web-test failure from the independent archive-path mismatch found by comparing the previous ZIP with the current replacement workflow's validation requirements. The corrected archive has been checked locally against the replacement script and its source-level suites; only a new GitHub Actions run can confirm the remote full replacement, permissions, and resulting PR.
