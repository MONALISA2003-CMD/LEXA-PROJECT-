import { defineConfig } from '@playwright/test';

const baseURL = process.env.LEXA_BROWSER_BASE_URL || 'http://127.0.0.1:3000';
const storageState = process.env.LEXA_PHASE2_STORAGE_STATE
  || process.env.LEXA_PHASE8_STORAGE_STATE
  || process.env.LEXA_PHASE7_STORAGE_STATE
  || process.env.LEXA_PHASE7_REVERSAL_STORAGE_STATE
  || process.env.LEXA_PHASE7_APPROVAL_STORAGE_STATE
  || process.env.LEXA_PHASE6_STORAGE_STATE
  || process.env.LEXA_PHASE5_STORAGE_STATE
  || process.env.LEXA_PHASE4_STORAGE_STATE
  || { cookies: [], origins: [] };
const stagingWritesEnabled = [
  'LEXA_PHASE2_ALLOW_STAGING_WRITES',
  'LEXA_PHASE5_ALLOW_STAGING_WRITES',
  'LEXA_PHASE6_ALLOW_STAGING_WRITES',
  'LEXA_PHASE7_ALLOW_STAGING_WRITES',
  'LEXA_PHASE7_REVERSAL_ALLOW_STAGING_WRITES',
  'LEXA_PHASE7_APPROVAL_ALLOW_STAGING_WRITES',
  'LEXA_PHASE7_ALLOCATION_ALLOW_STAGING_WRITES',
  'LEXA_PHASE8_ALLOW_STAGING_WRITES',
].some((key) => process.env[key] === '1');

const moduleAcceptancePattern = /(sales-sales|inventory-inventory|approvals-purchasing|approvals-authorization|finance-reports)-acceptance\.spec\.ts$/;
const workflowTransactionAcceptancePattern = /workflow-transaction-acceptance\.spec\.ts$/;
const approvalsReversalAcceptancePattern = /approvals-reversal-acceptance\.spec\.ts$/;
const approvalsApprovalAcceptancePattern = /approvals-approval-limits-acceptance\.spec\.ts$/;
const approvalsAllocationAcceptancePattern = /approvals-partial-allocations-acceptance\.spec\.ts$/;

export default defineConfig({
  testDir: './e2e',
  // Write-enabled reversal tests are a separate explicit matcher and remain
  // fail-closed behind their own staging host, role and disposable-fixture checks.
  testMatch: [moduleAcceptancePattern, workflowTransactionAcceptancePattern, approvalsReversalAcceptancePattern, approvalsApprovalAcceptancePattern, approvalsAllocationAcceptancePattern],
  globalSetup: './e2e/global-setup.ts',
  fullyParallel: false,
  workers: 1,
  retries: stagingWritesEnabled ? 0 : (process.env.CI ? 1 : 0),
  reporter: 'list',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  outputDir: stagingWritesEnabled ? 'test-results/staging-acceptance' : 'test-results/safe-contracts',
  use: {
    baseURL,
    storageState,
    browserName: 'chromium',
    headless: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
