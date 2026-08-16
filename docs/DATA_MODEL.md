# Data model

## `location`

The location is the only required source input. It includes identity, service area, URLs, services, budget, lead definition, tracking state, approved claims, LSA eligibility, and deployment safety flags.

## Generated plan

`render_plan.py` emits a review document containing:

- measurement gate and blockers
- channel budget hypothesis
- Search campaign settings
- enabled service ad groups and keyword destinations
- geographic targets and exclusions
- approval record placeholders

## Private runtime values

The following belong only in the destination agent's private runtime/configuration and must not be committed:

- Google Ads customer ID
- OAuth/developer credentials
- conversion action IDs/labels
- GTM/GA4 IDs
- phone numbers and CRM identifiers tied to a real location
- private exports and screenshots
