# Location-specific copy drafts

`examples/rsa-copy.yaml` is a generic slot library. The copy-draft renderer
turns a validated location config into actual reviewable RSA copy for each
enabled service.

## Generate a draft

Keep the real location config private and render the output into the ignored
`reports/` directory:

```bash
python scripts/validate_location.py config/local-location.yaml
python scripts/render_copy_draft.py config/local-location.yaml \
  --out reports/<location-slug>-rsa-copy-draft.md
```

The renderer produces:

- 15 headline candidates per enabled service;
- 4 description candidates per enabled service;
- the service ad group, landing page, and configured keyword seeds;
- character counts for every headline and description;
- configured offer/guarantee/review variants that were not selected; and
- service-level and final approval checklists.

## What the renderer may use

Core copy is generated from the location's:

- approved public brand name;
- city and state;
- enabled service name;
- service landing page;
- ad-group name; and
- configured keyword seeds.

Configured values under `claims.approved_offers`,
`claims.approved_guarantees`, and `claims.approved_review_claims` may be
included as optional variants when they fit the character limit. The renderer
does not invent prices, discounts, guarantees, review counts, response-time
promises, or service-area claims.

## Limits and approval

The draft enforces the common Google Ads RSA text limits used by this template:

- headline: 30 characters maximum;
- description: 90 characters maximum;
- 15 headline slots and 4 description slots per enabled service.

Character fit is not the same as approval. Before deployment, the location owner
must verify:

1. the service is actually sold and fulfilled in the target area;
2. the final URL matches the service and location;
3. every keyword and copy line matches the landing page;
4. every offer or claim is substantiated and policy-safe;
5. phone handling, hours, and lead routing are ready; and
6. the exact copy appears in the human-approved Google Ads diff.

The output is a draft only. It does not create ads, enable campaigns, alter
bidding, or modify conversion settings.
