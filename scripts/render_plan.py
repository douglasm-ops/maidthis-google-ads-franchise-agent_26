#!/usr/bin/env python3
"""Render a deterministic, reviewable deployment plan from a validated location YAML."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import yaml
from validate_location import validate

def money(v): return f"${v:,.2f}"
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("config"); ap.add_argument("--out", required=True); args=ap.parse_args()
    data=yaml.safe_load(Path(args.config).read_text()); errors=validate(data)
    if errors:
        print("Refusing to render invalid config:", file=sys.stderr)
        for e in errors: print(f"- {e}", file=sys.stderr)
        return 1
    l=data["location"]; b=l["budget"]; total=float(b["monthly_total"]); daily=total/30.4
    rows=[]
    for name,share in (("Search",b["search_share"]),("P-Max",b["pmax_share"]),("LSA",b["lsa_share"]),("Demand Gen",b["demand_gen_share"])):
        status="Not in v1" if name=="Demand Gen" else "Paused until approval"
        rows.append(f"| {name} | {float(share):.0%} | {money(daily*float(share))} | {status} |")
    services=[s for s in l["services"] if s.get("enabled")]
    adgroups="\n".join(f"- **{s['ad_group']}** — {', '.join(s['keywords'])} → {s['landing_page']}" for s in services)
    md=f"""# Deployment plan — {l['brand_name']} / {l['city']}, {l['state']}

**Status:** DRY RUN · campaigns paused · human approval required  
**Generated from:** `{Path(args.config).name}`  

## Measurement gate

- Canonical form event: `{l['tracking']['canonical_form_event']}`
- Canonical call event: `{l['tracking']['canonical_call_event']}`
- Qualified call threshold: `{l['lead_definition']['qualified_call_duration_seconds']} seconds`
- CRM receipt verified: `{l['tracking']['crm_receipt_verified']}`
- Enhanced conversions reviewed: `{l['tracking']['enhanced_conversions_reviewed']}`
- **Gate result:** `{'PASS' if l['tracking']['crm_receipt_verified'] else 'BLOCKED — verify a real form/call in CRM before enabling automated bidding'}`

## Campaign plan

| Channel | Share | Daily budget | Status |
|---|---:|---:|---|
{chr(10).join(rows)}

## Search structure

Campaign: `{l['city']} | Leads | {l['brand_name']}`  
Location mode: `PRESENCE`  
Google Search: ON · Display Network: OFF · Search Partners: controlled test  

### Enabled service groups

{adgroups}

## Geo plan

- Core cities: {', '.join(l['service_area'].get('cities',[])) or 'none'}
- Core postal codes: {', '.join(l['service_area'].get('postal_codes',[])) or 'none'}
- Exclusions: {', '.join(l['service_area'].get('excluded_areas',[])) or 'none'}

## Launch blockers

- [ ] Human approves this plan and the exact Google Ads diff.
- [ ] Form success creates exactly one canonical conversion and reaches the CRM.
- [ ] Qualified call conversion is tested and deduplicated.
- [ ] Landing page, phone, service area, claims, and hours are approved.
- [ ] Ads, keywords, negatives, assets, and destination URLs pass policy/QA.

## Approval record

- Approver: `[ ]`
- Approval timestamp: `[ ]`
- Destination customer ID: `[NEVER COMMIT — supply through the connected integration]`
- Deployment run ID: `[ ]`
"""
    Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(md); print(f"WROTE {args.out}")
if __name__=="__main__": main()
