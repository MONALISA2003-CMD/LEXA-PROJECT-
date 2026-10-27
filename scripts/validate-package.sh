#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python -m pytest -q tests
python -m compileall -q apps/api/app scripts
node --test tests/workspace-tenant-acceptance.test.mjs
if command -v tsc >/dev/null 2>&1; then
  (cd fixtures/typecheck && tsc --noEmit -p tsconfig.json)
else
  echo "SKIPPED: TypeScript contract fixture check (tsc is not installed)." >&2
fi
