# Data model

## `location`

The location is the only required source input. It includes identity, service area, URLs, services, budget, lead definition, tracking state, approved claims, LSA eligibility, and deployment safety flags.

## Generated copy draft

`render_copy_draft.py` emits a review-only Markdown worksheet for every enabled
service. Each service receives 15 headline candidates, 4 description candidates,
the configured keyword seeds, its ad group and landing page, character counts,
and approval checklists. Core copy is derived from the location config; optional
offers and claims are used only when configured and within the character limit.

## Generated plan

`render_plan.py` emits a review document containing:

- measurement gate and blockers
- channel budget hypothesis
- Search campaign settings
- enabled service ad groups and keyword destinations
- geographic targets and exclusions
- approval record placeholders
- service-level RSA copy candidates and approval checklists (when the copy renderer is run)

## Private runtime values

The following belong only in the destination agent's private runtime/configuration and must not be committed:

- Google Ads customer ID
- OAuth/developer credentials
- conversion action IDs/labels
- GTM/GA4 IDs
- phone numbers and CRM identifiers tied to a real location
- private exports and screenshots
