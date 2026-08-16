# Implementation guide

## 1. Intake

Collect `config/location.yaml` from the franchise operator. Do not accept a free-form brief as the only source of truth; the structured config prevents missing phone, service-area, lead-definition, and approval inputs.

Required decisions:

- Which services are actually sold and fulfilled?
- Which cities/ZIPs are inside the service area?
- When are calls answered and how are after-hours forms handled?
- What is one qualified form and one qualified call?
- What monthly budget and qualified-CPL target are approved?
- Which guarantees, offers, review counts, and proof points are legally approved?

## 2. Validate and render

```bash
python scripts/validate_location.py config/location.yaml
python scripts/render_plan.py config/location.yaml --out reports/location-plan.md
```

A plan that fails validation must not be sent to Google Ads.

## 3. Build Search

1. Create a Search lead-generation campaign named `[City] | Leads | [Brand]`.
2. Set the initial status to PAUSED.
3. Use Maximize Conversions with no target CPA until primary conversion quality is verified.
4. Turn Google Search on and Display Network off.
5. Use Presence targeting for the approved service area.
6. Create one ad group per enabled service intent.
7. Start with Exact and Phrase keywords mapped to the correct page.
8. Add reviewed campaign negatives and ad-group routing negatives.
9. Add one complete RSA per enabled ad group: 12–15 headlines and 4 descriptions.
10. Add reviewed sitelinks, callouts, structured snippets, and call assets.

Generate a location-specific copy worksheet before creating ads:

```bash
python scripts/render_copy_draft.py config/local-location.yaml \
  --out reports/<location-slug>-rsa-copy-draft.md
```

The renderer produces 15 headline candidates and 4 description candidates for
each enabled service, with character counts and configured keyword/landing-page
context. It uses only location-configured facts and approved claim fields; it
does not invent prices, offers, guarantees, review counts, or service-area
claims. Treat the output as a draft and include the exact reviewed copy in the
human approval diff.

## 4. Build P-Max

1. Create `[City] | Leads | [Brand] | PMax` paused.
2. Use one coherent core-service asset group first.
3. Use the location landing page and Presence targeting.
4. Supply text, landscape/square/portrait image, logo, and purpose-built video assets.
5. Add only substantiated claims and approved destinations.
6. Do not use P-Max as a substitute for broken measurement.

## 5. LSA and Demand Gen

LSA is a separate platform onboarding path. Enable only when the category/location is eligible, verification is complete, and lead handling is ready. Demand Gen is excluded from v1; add it only with an explicit awareness/remarketing hypothesis and a separate success metric.

## 6. Measurement gate

Before enabling campaigns or automated bidding:

- Run a test click and confirm UTMs.
- Submit the form and confirm exactly one canonical conversion plus CRM receipt.
- Place a test call and confirm the number, duration threshold, and exactly one conversion.
- Verify primary actions are included in Conversions and micro-events are Secondary.
- Check for duplicate tag/container/event implementations.
- Verify mobile UX because local lead traffic is commonly mobile-heavy.

## 7. Deployment

The external agent should produce a human-readable diff:

- campaigns and budgets
- ad groups and keywords
- negatives and match types
- ads and assets
- location targets and exclusions
- conversion actions/settings

It must wait for a human approval button or equivalent explicit approval. After applying approved writes, it must read the account back and report each resource's final status. Never trust a create/update response without verification.
