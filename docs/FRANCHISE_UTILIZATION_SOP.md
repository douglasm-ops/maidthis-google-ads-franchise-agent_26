# Franchise utilization SOP

## Purpose

Use this repository to turn one franchise location's approved business inputs into
a reviewable Google Ads implementation plan. The repository is a blueprint and
safety layer, not an unattended deployment bot.

This SOP is for:

- a franchise owner supplying location and business inputs;
- an authorized marketing operator or external AI agent preparing the build; and
- a human approver who owns the final Google Ads decision.

It supports a dry-run planning workflow for Search, P-Max, and eligible Local
Services Ads (LSA). Demand Gen is intentionally not part of the v1 launch path.

## Non-negotiable rules

1. Keep the repository generic. Never commit a real customer ID, conversion
   label, phone number, OAuth token, developer token, CRM export, screenshot, or
   other private franchise data.
2. Keep each location's real configuration outside the public repository unless
   the repository has first been made private and the data owner has approved
   that change.
3. Start in `DRY_RUN` mode and create campaigns paused.
4. Require explicit approval of the exact deployment diff before any live write.
5. Use a read-only preflight before a write, and read the account back after every
   approved write.
6. Do not enable automated bidding until one canonical form conversion, one
   qualified-call conversion, and CRM receipt have been tested and reconciled.
7. Do not copy the parent location's conversion setup, location targets, claims,
   phone number, or private account data into a new franchise config.

## Roles and access

### Franchise owner

- Supplies accurate services, service area, hours, phone, landing pages, budget,
  offers, claims, lead definition, and CRM owner.
- Confirms which services the location can actually fulfill.
- Approves the final plan and the exact Google Ads change list.
- Owns lead response after launch.

### Marketing operator or external AI agent

- Uses the repository's schema, validator, and renderer.
- Performs planning and read-only checks first.
- Produces a human-readable approval packet.
- Does not bypass the approval gate or store secrets in Git.

### Human approver

- Confirms the destination account identity and change scope.
- Reviews measurement, targeting, copy, assets, budget, and rollback plan.
- Gives explicit approval naming the account and exact proposed diff.

## Prerequisites

Before starting, confirm:

- A Google Ads account exists for the franchise location.
- The operator has authorized access to that account, preferably through a
  least-privilege client-level connection rather than a broad manager account.
- A public HTTPS landing page exists for the location and each enabled service.
- The location has an approved business phone and a separate tracking phone if
  call tracking is used.
- The service area, exclusions, business hours, response owner, and lead-routing
  process are known.
- The franchise owner has approved the monthly budget and qualified-CPL target.
- The form, call, and CRM owners can test conversion receipt.
- Python 3.11+ and Git are available locally, or the operator can use an
  equivalent isolated environment.

The repository's GitHub Actions workflow validates the generic example on pushes
and pull requests. A green workflow does not authorize a live Google Ads change.

## Step 1 — Get the repository

Use the repository's **Code** menu to clone it, or download a copy from the
approved repository URL. Work from a branch or a private local copy; do not put
real location data on the public `main` branch.

```bash
git clone <approved-repository-url>
cd maidthis-google-ads-franchise-agent_26
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install pyyaml
```

The repository's GitHub Actions workflow should show a green check after the
initial setup. If it does not, fix the repository or environment issue before
using the plan as an operating input.

## Step 2 — Prepare the private location config

Copy the example to a private, ignored path:

```bash
cp examples/baltimore-location.yaml config/local-location.yaml
```

If the repository is public, do **not** commit `config/location.yaml`. The
`.gitignore` already excludes `config/local.*` and `config/private.*`; add a
local filename or keep the file outside the repository. Before using a file,
replace every demonstration value.

Complete these sections in `config/local-location.yaml`:

| Section | What the franchise must provide |
|---|---|
| `location` | Slug, brand, legal entity, city/state, timezone, currency, phone, landing page |
| `service_area` | Approved cities, ZIP/postal codes, exclusions, and `PRESENCE` targeting |
| `services` | Only services actually sold; each enabled service needs a page, ad-group name, and keywords |
| `budget` | Monthly total and channel shares; v1 Demand Gen share must be `0.0` |
| `lead_definition` | Canonical form event, qualified-call duration, and CRM qualification stage |
| `tracking` | Canonical form/call events, owners, UTM template, and CRM verification state |
| `claims` | Only approved guarantees, review claims, and offers |
| `lsa` | Eligibility and verification; do not enable LSA prematurely |
| `deployment` | Keep `DRY_RUN`, `create_campaigns_paused: true`, and `require_human_approval: true` |

Use the authoritative comments in
[`config/location.schema.yaml`](../config/location.schema.yaml) as the field
reference. Do not use the Baltimore example's cities, ZIP codes, URLs, phone,
claims, or conversion details as a new location's defaults.

## Step 3 — Validate before planning

Run:

```bash
python scripts/validate_location.py config/local-location.yaml
```

Expected success output includes:

```text
VALID LOCATION CONFIG
- deployment: DRY_RUN / paused campaigns / human approval required
```

If validation fails, stop. Correct the config and run the validator again. Do
not send an invalid config to an AI agent or Google Ads integration.

Common validation blockers include:

- missing required fields;
- a non-HTTPS URL or invalid phone format;
- no enabled service or service without keywords;
- service-area mode other than `PRESENCE`;
- budget total of zero, channel shares that do not sum to 1.0, or nonzero
  Demand Gen share;
- qualified-call threshold below 30 seconds;
- missing canonical tracking events;
- deployment mode not `DRY_RUN`, campaigns not paused, or approval disabled; and
- LSA enabled without both eligibility and verification.

## Step 4 — Render the review plan

Create a private output directory and render the plan:

```bash
mkdir -p reports
python scripts/render_plan.py config/local-location.yaml \
  --out reports/<location-slug>-deployment-plan.md
```

Review the generated plan as a human-readable draft. It must show:

- the measurement gate and whether CRM receipt is verified;
- the channel budget hypothesis;
- Search campaign and service ad groups;
- location targets and exclusions;
- launch blockers; and
- approval placeholders.

If the measurement gate is blocked, the plan is still useful for preparation,
but campaigns must remain paused and automated bidding must not be enabled.

## Step 5 — Have the agent prepare, not deploy

Give the external AI agent:

1. the validated private config through its approved secure runtime;
2. the rendered plan;
3. read-only access to the destination Google Ads account, if available; and
4. this repository's safety rules.

Ask the agent to produce a deployment draft containing:

- destination account identity;
- campaign names, types, statuses, and budgets;
- locations and exclusions;
- ad groups, keywords, match types, and negatives;
- ads, assets, final URLs, and substantiated claims;
- conversion actions used for bidding/reporting;
- measurement test results and known gaps; and
- rollback or pause steps.

The agent must not infer private IDs from the public example, create an
unapproved location target, reuse unapproved claims, or treat a green GitHub
Actions run as deployment approval.

## Step 6 — Perform the read-only preflight

Before a live write, verify privately:

- the Google Ads customer and location identity;
- account currency and timezone;
- existing campaigns and naming collisions;
- service-area eligibility and location targets;
- landing-page availability and HTTPS;
- conversion actions and primary/secondary settings;
- CRM receipt path;
- policy or disapproval history; and
- available budget and bidding constraints.

The first Search build should normally use one consolidated lead-generation
campaign, Presence targeting, Search enabled, Display Network off, and one
ad group per true service intent. Start with Exact and Phrase keywords mapped to
the right service page. Add P-Max only after measurement and asset QA. Add LSA
only after eligibility, verification, and lead handling are ready.

## Step 7 — Review and approve the exact diff

The human approver must compare the rendered plan and agent draft with the
actual read-only preflight. Approval must name:

- the destination Google Ads account;
- the campaigns and resources in scope;
- the approved budget and status;
- the approved measurement actions; and
- any explicit exceptions.

“Go ahead” without an identified account and exact change scope is not enough.
Save the approval record privately. If anything changes after approval, produce
a new diff and obtain approval again.

## Step 8 — Apply approved changes safely

Only the authorized operator or approved deployment agent may write to Google
Ads. Keep new campaigns paused. Apply only the approved diff. Do not:

- enable campaigns before the owner is ready;
- change budgets or bidding outside the approved scope;
- add unreviewed keywords or negatives;
- publish unsupported claims or offers; or
- turn on automated bidding against unverified conversions.

After each write, perform a follow-up read. Record the resource name/ID,
requested state, actual state, and any warning. Keep the verification report
private.

## Step 9 — Complete measurement QA

Before enabling campaigns or automated bidding:

1. Test a click and confirm the intended UTM values.
2. Submit the form on mobile and desktop.
3. Confirm exactly one canonical form conversion.
4. Confirm the form lead reaches the CRM and the expected stage.
5. Place a test call and confirm the number, duration threshold, and exactly one
   qualified-call conversion.
6. Check primary versus secondary conversion settings.
7. Check for duplicate tags, GTM containers, events, or CRM automations.
8. Confirm after-hours routing and the lead-response owner.

If any test fails, keep campaigns paused, document the failure, and fix
measurement before scaling or enabling automated bidding.

## Step 10 — Launch and monitor the first 30 days

After the owner approves the QA result, enable only the approved campaigns and
record the launch time. Keep a private weekly log covering:

- spend and pacing versus budget;
- qualified forms and qualified calls;
- cost per qualified lead;
- CRM receipt and lead quality;
- search terms and negative-keyword opportunities;
- location performance and out-of-area leads;
- asset/ad policy status and fatigue;
- landing-page and call-answer issues; and
- changes made, approver, and date.

Use qualified leads and downstream outcomes, not platform-reported volume alone,
to judge performance. Do not make large budget or bidding changes while
measurement is uncertain. Pause or escalate if tracking breaks, lead quality
collapses, policy risk appears, or the location cannot service the traffic.

## Security and data handling

Never commit:

- Google Ads customer IDs;
- OAuth, developer, or refresh tokens;
- conversion IDs/labels;
- GTM/GA4 IDs;
- real phone numbers or CRM identifiers tied to a location;
- lead exports, search-term exports, or screenshots; or
- private approval records.

Use the connected integration's secret manager or private runtime. Before
sharing a branch, pull request, log, or screenshot, scan it for private values.
If a secret is accidentally committed, stop, rotate/revoke it, remove it from
Git history using an approved process, and notify the account owner.

## Troubleshooting

### The validator says the config is invalid

Read every listed error, correct the private YAML, and rerun the validator.
Do not bypass the validator or edit the generated plan to hide a blocker.

### The plan renderer refuses to run

The renderer validates the config first. Fix the same validation errors, ensure
PyYAML is installed, and rerun the command from the repository root.

### GitHub Actions is red

Open the failed workflow run, identify the failed step, and fix the repository
or dependency issue. A green local command is not a substitute for a failed
repository check. The workflow validates the generic example only.

### The agent asks for a customer ID or credential

Provide it only through the approved private integration/runtime. Never add it
to YAML committed to GitHub, an issue, a pull request, a chat transcript, or a
generated public report.

### The destination account cannot be confirmed

Stop. Do not create or modify campaigns. Resolve account ownership and access
with the franchise owner or authorized Google Ads administrator.

### Form or call tests do not reach the CRM

Keep campaigns paused. Record the test timestamp, path, expected event, observed
event, and CRM result. Repair the form/call/CRM path and repeat the complete
measurement QA sequence.

### A live change was made outside the approved diff

Pause the affected resource if safe, notify the human approver, capture the
actual account state, and reconcile the diff before any further change.

## Completion criteria

A franchise handoff is complete only when:

- the private config validates;
- the plan renders and is reviewed;
- read-only preflight confirms the destination account;
- the exact diff is approved;
- campaigns are created paused;
- form, call, CRM, and UTM tests reconcile;
- every write has been verified by a follow-up read; and
- the private launch and monitoring record is saved.

The repository's
[`docs/HANDOFF_CHECKLIST.md`](HANDOFF_CHECKLIST.md) is the final sign-off
checklist. The franchise should retain its private config, approval, account
access record, QA evidence, and monitoring log outside the public repository.
