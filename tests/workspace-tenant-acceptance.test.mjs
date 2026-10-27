import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
const root = new URL('../', import.meta.url).pathname;
const read = p => readFileSync(join(root, p), 'utf8');

test('workspace and onboarding pages surface API failures and let users resume setup', () => {
  const workspace = read('apps/web/app/workspace/page.tsx');
  const onboarding = read('apps/web/app/onboarding/page.tsx');
  assert.match(workspace, /Could not load your workspaces/);
  assert.match(workspace, /selectWorkspace\(item\.tenant_id\)/);
  assert.match(onboarding, /Setup progress could not be verified/);
  assert.match(onboarding, /getSetupProgress/);
  assert.match(onboarding, /resume_path/);
  assert.match(onboarding, /Set up missing details/);
});

test('team UI uses owner-managed helpers and handles one-time invitation links safely', () => {
  const page = read('apps/web/app/administration/members/page.tsx');
  assert.match(page, /createWorkspaceInvitation/);
  assert.match(page, /replaceWorkspaceMemberBranches/);
  assert.match(page, /revokeWorkspaceInvitation/);
  assert.match(page, /navigator\.clipboard\.writeText/);
  assert.match(page, /one-time invitation link/i);
  assert.match(page, /PENDING/);
});

test('invite page reads token from fragment, removes it from history, previews, then accepts', () => {
  const page = read('apps/web/app/invite/page.tsx');
  const api = read('apps/web/lib/api.ts');
  assert.match(page, /previewWorkspaceInvitation/);
  assert.match(page, /acceptWorkspaceInvitation/);
  assert.match(page, /window\.location\.hash/);
  assert.match(page, /replaceState/);
  assert.match(page, /expires_at/);
  assert.match(page, /Ask the workspace owner to issue a new link/);
  assert.match(api, /invitations\/preview/);
  assert.match(api, /invitations\/accept/);
  assert.match(api, /JSON\.stringify\(\{ token \}\)/);
  assert.match(api, /method: "POST"/);
});

test('workspace schema migration is tenant-isolated and migration application remains a separate gate', () => {
  const migration = read('migrations/030_phase3_workspace_memberships.sql');
  assert.match(migration, /ADDitive ONLY/i);
  assert.match(migration, /FORCE ROW LEVEL SECURITY/);
  assert.match(migration, /lexa_list_active_user_workspaces/);
  assert.match(migration, /lexa_find_workspace_invitation/);
  assert.match(migration, /Validate on a clean isolated database/);
  assert.match(migration.toLowerCase(), /do not create duplicate parallel invitation\/branch-assignment tables/);
});
