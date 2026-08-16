# MaidThis Google Ads Franchise Agent

A safe, location-specific implementation kit for launching local lead-generation campaigns in Google Ads. An external AI agent can use this repository to collect a franchise location's inputs, generate a proposed build, validate the plan, and hand it to a human for approval before any live change.

> **This repository is a blueprint and safety layer—not an unattended deployment bot.** Live Google Ads writes must remain behind an explicit human approval step and the connected account's own permissions.

## What this repo does

- Converts a location brief into a structured Google Ads build plan.
- Provides reusable Search, P-Max, Local Services Ads, measurement, keyword, negative-keyword, ad-copy, asset, and launch-QA templates.
- Renders a location-specific, review-only RSA copy draft with 15 headlines and 4 descriptions per enabled service.
- Validates required inputs and blocks unsafe configurations before deployment.
- Defaults to **dry run** and **paused campaign creation**.
- Separates generic franchise patterns from location-specific values.

## What this repo does not do

- It does not contain credentials, Google Ads customer IDs, conversion labels, phone numbers, private account exports, or live account data.
- It does not assume that the parent Baltimore account's conversion setup is safe to copy.
- It does not enable campaigns, alter budgets, add keywords, or change bidding without a human-approved deployment plan.
- It does not promise a benchmark CPA/CPL; every location must establish its own qualified-lead definition and targets.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
python scripts/validate_location.py examples/baltimore-location.yaml
python scripts/render_plan.py examples/baltimore-location.yaml --out reports/baltimore-plan.md
python scripts/render_copy_draft.py examples/baltimore-location.yaml --out reports/baltimore-rsa-copy-draft.md
```

The example is intentionally a **generic Baltimore demonstration**. Replace it before use. It contains no real customer ID or conversion label.

## Agent workflow

1. **Collect** `config/location.yaml` from the franchise owner.
2. **Validate** the location config with `scripts/validate_location.py`.
3. **Generate** a plan with `scripts/render_plan.py`.
4. **Generate** a copy draft with `scripts/render_copy_draft.py`; review each service's headlines, descriptions, keyword seeds, and landing page.
5. **Review** the measurement gate, service area, budget, claims, keywords, negatives, and landing page.
6. **Run a read-only preflight** against the destination Google Ads account, if the integration is connected.
7. **Create a deployment draft only**: campaigns and ads should start paused; no live write should execute automatically.
8. **Request human approval** with a complete change list.
9. **Apply approved changes** using the destination account's authenticated integration.
10. **Verify** every write with a follow-up read and save the verification report privately.

## Recommended v1 architecture

- **Search**: one consolidated lead-generation campaign, separated into ad groups by true service intent.
- **P-Max**: one coherent lead-generation campaign/asset group after assets and measurement pass QA.
- **LSA**: add only where the service/category/location is eligible and onboarding is complete.
- **Demand Gen**: keep out of v1 until primary conversions and qualified-lead quality are stable.

See [`docs/IMPLEMENTATION_GUIDE.md`](docs/IMPLEMENTATION_GUIDE.md) for the full operating procedure and [`docs/SAFETY_AND_APPROVALS.md`](docs/SAFETY_AND_APPROVALS.md) for deployment rules.
For a step-by-step franchise handoff, see [`docs/FRANCHISE_UTILIZATION_SOP.md`](docs/FRANCHISE_UTILIZATION_SOP.md).
For location-specific RSA drafts, see [`docs/COPY_DRAFTS.md`](docs/COPY_DRAFTS.md).

## Repository map

```text
config/
  location.schema.yaml       # Human/agent contract for required inputs
  location.yaml              # Copy from the example; keep local/private
examples/
  baltimore-location.yaml    # Safe, fictionalized example
  rsa-copy.yaml              # Generic copy slots
  keyword-plan.yaml          # Generic keyword worksheet
  negative-plan.yaml         # Generic negative/routing worksheet
docs/
  IMPLEMENTATION_GUIDE.md    # Build sequence and Google Ads settings
  COPY_DRAFTS.md             # Generate and review location-specific RSA drafts
  SAFETY_AND_APPROVALS.md    # Dry-run, approval, credential, and verification policy
  DATA_MODEL.md              # Location config and generated plan semantics
  HANDOFF_CHECKLIST.md       # Human launch checklist
  FRANCHISE_UTILIZATION_SOP.md # Step-by-step franchise operating procedure
  SOURCES_AND_ASSUMPTIONS.md # What was generalized from the Baltimore model
  CI_WORKFLOW_TEMPLATE.yml   # Copy to .github/workflows/ after workflow scope is granted
schemas/
  deployment-plan.schema.json
scripts/
  validate_location.py       # Deterministic config validator
  render_plan.py             # Deterministic plan renderer
  render_copy_draft.py       # Deterministic, review-only RSA copy renderer
```

## Security

Never commit `.env`, OAuth tokens, developer tokens, refresh tokens, customer IDs, conversion labels, phone numbers, CRM exports, search-term exports, or private screenshots. Use the destination agent's secret manager and integration permissions. See [`SECURITY.md`](SECURITY.md).

## License

MIT. The operating guidance and brand-specific materials remain subject to the franchise agreement and MaidThis approval.
