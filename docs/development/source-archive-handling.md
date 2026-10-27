# Source archive handling

The repository's supported full-tree replacement workflow is `.github/workflows/replace-from-archive.yml`. It uses `scripts/replace_from_archive.py` to checksum and validate a source ZIP, check the exact expected `main` HEAD, preserve a pre-replacement backup artifact, and open a reviewable pull request by default. It does not extract arbitrary ZIP files uploaded into the repository. The former `.github/workflows/lexa-zip-extract.yml` workflow is not part of the current repository.

## Archive layout required by the existing workflow

Create the ZIP at the repository root, without a wrapper folder. Entries should begin with canonical top-level paths such as `apps/`, `migrations/`, `docs/`, `.github/`, `scripts/`, and `README.md`. The validator requires these exact root paths:

- `README.md`
- `apps/web/package.json`
- `apps/api/app/main.py`
- `migrations/README.md`
- `.github/workflows/ci.yml`
- `.github/workflows/replace-from-archive.yml`

The CI workflow is named `ci.yml` because the pre-existing replacement script validates that exact path. Keep path references and contract tests aligned with it.

## Applying a replacement

1. Publish the exact ZIP as a GitHub Release asset and copy its HTTPS asset URL.
2. Compute the checksum for that file using `sha256sum LEXA-cleaned.zip`.
3. In GitHub, open **Actions → Replace repository from verified source archive → Run workflow**.
4. Supply `target_branch=main`, the asset URL, the 64-character SHA-256 checksum, and the current full 40-character expected `main` head SHA.
5. Set the required confirmation to `REPLACE_ALL_FILES`. Use `pull_request` mode (the default), not `direct` mode.
6. Review the resulting pull request, deletion list, source diff, and CI results before merging.

## Safety properties

- Rejects ZIPs with a wrong checksum, duplicate or case-colliding paths, traversal/absolute paths, symlinks, Git metadata, too many entries, or oversized content.
- Requires an exact current target-branch HEAD and refuses a stale run.
- Requires explicit `REPLACE_ALL_FILES` confirmation; default `NO` refuses replacement.
- Creates a ZIP backup of the previous source tree as a retained workflow artifact.
- Replaces the complete source tree while preserving `.git`; this is necessary to remove obsolete project snapshots rather than leave them behind as an overlay extraction would.
- Does not bypass branch-protection rules. CI, GitHub permissions, or policy restrictions can still fail and must be reviewed.

Do not put credentials, `.git`, `node_modules`, caches, generated build output, nested ZIPs, or production data in the archive. Deleting a credential from the ZIP does not revoke it or remove it from Git history.
