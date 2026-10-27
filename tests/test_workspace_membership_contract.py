from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "apps/api/app/routes/workspace_context.py"
MEMBERS = ROOT / "apps/api/app/routes/membership_admin.py"
MIGRATION = ROOT / "migrations/030_phase3_workspace_memberships.sql"
API_TS = ROOT / "apps/web/lib/api.ts"


def test_workspace_switch_checks_server_authoritative_active_membership_list():
    source = WORKSPACE.read_text()
    assert "lexa_list_active_user_workspaces" in source
    assert 'raise HTTPException(status_code=403, detail="You do not have an active membership in that workspace")' in source
    assert 'Tenant.status == "ACTIVE"' in source


def test_switch_revokes_old_session_before_changing_tenant_rls_context():
    source = WORKSPACE.read_text()
    revoked = source.index("old_session.revoked_at = now")
    assert revoked < source.index("db.flush()", revoked)
    assert source.index("db.flush()", revoked) < source.index("set_config('app.tenant_id', :tenant_id", revoked)


def test_setup_progress_uses_persisted_tenant_scoped_resources():
    source = WORKSPACE.read_text()
    for model in ("BusinessProfile", "Warehouse", "Location", "Branch"):
        assert model in source
    assert "setup_progress(" in source
    assert "tenant.setup_completed" not in source
    assert 'Warehouse.status == "ACTIVE"' in source
    assert "Location.warehouse_id.in_(warehouse_ids)" in source
    assert 'currency_configured=' in source


def test_membership_mutation_is_tenant_scoped_and_protects_owner_access():
    source = MEMBERS.read_text()
    assert "TenantMembership.tenant_id == tenant_id" in source
    assert "UPDATE sessions SET revoked_at = now() WHERE tenant_id = :tenant_id AND user_id = :user_id" in source
    assert "_active_owner_count(db, tenant_id) <= 1" in source
    assert "pg_advisory_xact_lock" in source
    assert 'require_active_workspace_permission("members.manage")' in source
    assert 'require_active_workspace_permission("members.read")' in source


def test_branch_assignment_rejects_foreign_or_inactive_branches():
    source = MEMBERS.read_text()
    assert "Branch.tenant_id == tenant_id" in source
    assert 'Branch.status == "ACTIVE"' in source
    assert "MembershipBranchAssignment" in source


def test_invitation_tokens_are_hashed_and_not_added_to_outbox_payloads():
    source = MEMBERS.read_text()
    assert "token_hash=invitation_token_digest(token)" in source
    assert '"invite_url": "/invite#token=" + quote(token)' in source
    assert '@invitations_router.post("/preview")' in source
    assert "def invitation_preview(body: InvitationPreviewIn" in source
    assert 'payload={"invitation_id": str(row.id), "email": email' in source
    assert '"token": token' not in source
    assert "finish_idempotency(db, idem, status_code=201, response_body=stored_response" in source


def test_invitation_acceptance_checks_hash_expiry_status_and_email_identity():
    source = MEMBERS.read_text()
    assert "lexa_find_workspace_invitation(:token_hash)" in source
    assert "WorkspaceInvitation.token_hash == token_hash" in source
    assert "invitation_is_expired(invitation.expires_at)" in source
    assert "func.lower(User.email) == invitation.email" in source
    assert 'invitation.status = "ACCEPTED"' in source


def test_migration_enforces_rls_and_limited_public_invitation_lookup():
    source = MIGRATION.read_text()
    assert "ALTER TABLE public.tenant_invitations ENABLE ROW LEVEL SECURITY" in source
    assert "ALTER TABLE public.tenant_invitations FORCE ROW LEVEL SECURITY" in source
    assert "ALTER TABLE public.membership_branch_assignments ENABLE ROW LEVEL SECURITY" in source
    assert "ALTER TABLE public.membership_branch_assignments FORCE ROW LEVEL SECURITY" in source
    assert "lexa_find_workspace_invitation" in source
    assert "lexa_list_active_user_workspaces" in source
    assert "REVOKE ALL ON FUNCTION public.lexa_find_workspace_invitation(text) FROM PUBLIC" in source
    assert "GRANT EXECUTE ON FUNCTION public.lexa_find_workspace_invitation(text) TO lexa_app" in source
    assert "do not create duplicate parallel invitation/branch-assignment tables" in source.lower()


def test_frontend_helpers_expose_workspace_switch_setup_and_invitation_lifecycle():
    source = API_TS.read_text()
    for name in (
        "getWorkspaceOptions", "selectWorkspace", "getSetupProgress", "getWorkspaceMembers",
        "createWorkspaceInvitation", "acceptWorkspaceInvitation", "replaceWorkspaceMemberBranches",
        "previewWorkspaceInvitation", "revokeWorkspaceInvitation",
    ):
        assert name in source


def test_invitation_creation_prevents_duplicate_membership_and_unsafe_replay():
    source = MEMBERS.read_text()
    assert "func.lower(User.email) == email" in source
    assert "This account already has a membership in the invited workspace" in source
    assert '"invite_url": None, "replayed": True' in source
    assert 'row.status not in ("PENDING", "EXPIRED")' in source
    assert "Only a pending or expired invitation can be resent" in source


def test_invitation_acceptance_checks_tenant_active_state_and_case_insensitive_email():
    source = MEMBERS.read_text()
    assert 'select(Tenant).where(Tenant.id == tenant_id, Tenant.status == "ACTIVE")' in source
    assert 'raise HTTPException(status_code=404, detail="Invitation is invalid or expired")' in source
    assert "func.lower(User.email) == invitation.email" in source


def test_member_and_invitation_admin_require_active_workspace_permissions():
    source = MEMBERS.read_text()
    assert "def require_active_workspace_permission(permission_code: str)" in source
    assert 'Depends(require_active_workspace_permission("members.manage"))' in source
    assert 'Depends(require_active_workspace_permission("members.read"))' in source


def test_invitation_email_matching_is_case_insensitive():
    source = MEMBERS.read_text()
    assert source.count("func.lower(User.email) == email") >= 1
    assert "func.lower(User.email) == invitation.email" in source
