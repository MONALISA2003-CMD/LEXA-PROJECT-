# AI policy and routing boundary

This document describes the intended safety boundary for LEXA's current AI integration. It is not a claim that every proposed provider registry or routing feature is implemented.

## Current baseline

The active API includes central intelligence policy and assistant routes under `apps/api/app/intelligence/` and `apps/api/app/routes/`. External model execution is a separate capability from exposing an assistant endpoint; a provider key or model-name environment variable alone must not enable provider calls. Check the active policy and route code before changing provider behavior.

The intended baseline is fail-closed: provider execution should remain disabled unless an explicit, reviewed policy allows it. Do not send tenant-confidential data to external model services without documented classification, authorization, provider approval, bounded inputs/outputs, and auditability. Keep provider credentials server-side and enforce per-request resource limits.

## Review checklist for any future provider implementation

- Explicit configuration defaults to disabled and validates allowed provider/model values.
- The endpoint enforces authenticated workspace scope and applies rate/input/output limits.
- The route does not treat provider availability, model output, or a generated summary as authoritative business state.
- Sensitive tenant content is excluded unless the data policy and provider terms allow it.
- Timeouts, provider failures, invalid output, and quota exhaustion fail safely; raw secrets and confidential prompt content are not logged.
- A deterministic local fallback, when offered, has clearly defined capability and quality limits.
- Tests cover disabled-by-default behavior, authorization boundaries, malformed outputs, timeouts, and rate limits.

An unmerged model-registry implementation stored in the previous source archive has intentionally not been installed by this cleanup; its one-time mutator workflow was removed so code under `docs/` cannot silently rewrite live source or push directly to `main`.
