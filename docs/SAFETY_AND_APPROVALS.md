# Safety and approvals

## Non-negotiable defaults

- Dry run first.
- Create campaigns paused.
- Human approval required.
- No credentials in Git.
- No customer IDs or conversion labels in the generic repository.
- Read-only preflight before any write.
- Verify every write with a follow-up read.

## Approval packet

Before a write, the agent must show:

1. Destination account identity (provided privately, never committed).
2. Proposed campaign names/types/statuses/budgets.
3. Location targets and exclusions.
4. Keywords and match types.
5. Negative keywords and where they will apply.
6. Ads, assets, final URLs, and claims.
7. Conversion actions used for bidding/reporting.
8. Measurement test results and known gaps.
9. Rollback/pause plan.

Approval must name the destination account and exact scope. A vague “go ahead” is not sufficient for a live write.

## Block conditions

Stop if:

- The config is invalid.
- The destination account identity cannot be confirmed.
- Form/call conversions are not canonical or CRM receipt is unverified.
- Location targeting is not Presence for a local-only service.
- Display Network is enabled on the initial Search build without an explicit exception.
- A claim, offer, guarantee, phone, URL, or service is not approved.
- The request would expose a secret or private customer/franchise data.
- The user has not approved the exact proposed diff.

## Least privilege

Use a connected integration or secret manager. Prefer a separate destination account, a dedicated deployment identity, and permissions limited to the franchise account. Do not use a manager account to make broad changes when a client-level connection will do.
