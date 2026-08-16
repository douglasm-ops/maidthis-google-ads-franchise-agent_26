# Sources and assumptions

This repository generalizes the implementation pattern extracted from the MaidThis Cleaning of Baltimore Google Ads account. The live account was read-only inspected on 2026-08-16.

## Generalized patterns

- Consolidated Search lead-generation campaign with service-intent ad groups.
- P-Max lead-generation campaign with one coherent core asset group.
- Local Services Ads as a separate eligible/onboarding track.
- Google Search on, Display Network off, Presence targeting for local-only service.
- Complete RSA asset set and broad P-Max image/video/text coverage.
- Campaign-level universal negatives plus ad-group routing negatives.
- Maximize Conversions initially, with target CPA/value bidding deferred until verified data supports it.

## Deliberately excluded

- Real account/customer IDs, budgets tied to a real client, phone numbers, conversion IDs/labels, GTM/GA4 IDs, URLs containing private destinations, private exports, and claims.
- The source account's conversion-action sprawl.
- The source account's tracking implementation: an existing audit found multiple GTM containers, AJAX-form attribution risks, and website forms excluded from primary Conversions. That is treated as a failure mode to prevent, not a pattern to replicate.

## Budget note

The editable 32% Search / 38% P-Max / 30% LSA allocation is an observed starting hypothesis from the enabled source account's daily budgets, not a universal benchmark. Each location must replace it with its own approved budget and qualified-lead economics.
