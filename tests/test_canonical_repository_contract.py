from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repository_has_one_canonical_application_tree():
    assert (ROOT / "apps/web/package.json").is_file()
    assert (ROOT / "apps/api/app/main.py").is_file()
    assert (ROOT / "migrations/048_phase7_approval_limits_reversals_accounting.sql").is_file()
    for duplicate_root in (
        "source", "src", "lexa-final", "lexa_v280_src", "lexa_fix_audit",
        "LEXA-Phase1-2.9.1", "LEXA_Open_Development_v1.5.0",
        "LEXA_PHASE4_UX_RESET_IMPLEMENTATION_2026-10-21",
        "LEXA_Phase0_to_Phase3_Increments_01_06_Closure_2026-10-20",
        "LEXA_Phase1_Business_Kernel_v1.7.0", "LEXA_Phase2_Catalog_Hardening_v1.2.0",
        "LEXA_Phase3_Increment_01", "LEXA_Phase3_Increments_01_06",
        "LEXA_Phase4A_EndToEnd_v2.1.0", "LEXA_Phase4B_Accounting_EFRIS_v2.3.0",
        "phase0-2-evidence", "phase3-increments-01-03", "overrides", "artifacts",
    ):
        assert not (ROOT / duplicate_root).exists(), f"duplicate project root remains: {duplicate_root}"


def test_ci_and_archive_workflows_are_present_and_reviewable():
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    replacement = (ROOT / ".github/workflows/replace-from-archive.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in ci
    assert "api-unit-contracts" in ci and "web-build" in ci and "compose-config" in ci
    assert "archive_sha256" in replacement and "expected_head_sha" in replacement
    assert "confirmation" in replacement and "REPLACE_ALL_FILES" in replacement
    assert "write_mode" in replacement and "pull_request" in replacement


def test_deployment_liveness_and_readiness_remain_separate():
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    health = (ROOT / "apps/api/app/main.py").read_text(encoding="utf-8")
    assert "healthCheckPath: /health" in render
    assert '@app.get("/health", tags=["system"])' in health
    assert '@app.get("/ready", tags=["system"])' in health
    assert "REQUIRED_APP_MIGRATIONS" in (ROOT / "apps/api/app/health.py").read_text(encoding="utf-8")
