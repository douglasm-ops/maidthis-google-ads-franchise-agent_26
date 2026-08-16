#!/usr/bin/env python3
"""Validate a location config before any Google Ads planning or write step."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
import yaml

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PHONE = re.compile(r"^\+1-\d{3}-\d{3}-\d{4}$")
URL = re.compile(r"^https://")
REQUIRED = ["slug", "brand_name", "legal_business_name", "city", "state", "timezone", "currency", "phone", "landing_page", "service_area", "services", "budget", "lead_definition", "tracking", "deployment"]

def validate(data):
    errors=[]
    loc=data.get("location") if isinstance(data,dict) else None
    if not isinstance(loc,dict): return ["Missing top-level 'location' mapping"]
    for key in REQUIRED:
        if key not in loc: errors.append(f"location.{key} is required")
    if errors: return errors
    if not SLUG.match(str(loc["slug"])): errors.append("location.slug must be lowercase hyphenated")
    if len(str(loc["state"])) != 2 or not str(loc["state"]).isalpha(): errors.append("location.state must be a two-letter code")
    for field in ("landing_page",):
        if not URL.match(str(loc[field])): errors.append(f"location.{field} must use https://")
    for field in ("phone","tracking_phone"):
        if field in loc and not PHONE.match(str(loc[field])): errors.append(f"location.{field} must use +1-000-000-0000 format")
    sa=loc["service_area"]
    if sa.get("targeting_mode") != "PRESENCE": errors.append("service_area.targeting_mode must be PRESENCE for a local-only v1 build")
    if not sa.get("cities") and not sa.get("postal_codes"): errors.append("service_area needs at least one city or postal code")
    services=loc["services"]
    if not isinstance(services,list) or not services: errors.append("services must be a non-empty list")
    enabled=[]
    for i,s in enumerate(services if isinstance(services,list) else []):
        for k in ("name","enabled","landing_page","ad_group","keywords"):
            if k not in s: errors.append(f"services[{i}].{k} is required")
        if s.get("enabled"): enabled.append(s.get("name"))
        if s.get("landing_page") and not URL.match(str(s["landing_page"])): errors.append(f"services[{i}].landing_page must use https://")
        if not isinstance(s.get("keywords"),list) or not s.get("keywords"): errors.append(f"services[{i}].keywords must be non-empty")
    if not enabled: errors.append("at least one service must be enabled")
    b=loc["budget"]
    try: total=float(b.get("monthly_total",0)); shares=[float(b.get(x,0)) for x in ("search_share","pmax_share","lsa_share","demand_gen_share")]
    except (TypeError,ValueError): errors.append("budget values must be numeric"); total=0; shares=[]
    if total <= 0: errors.append("budget.monthly_total must be > 0")
    if shares and abs(sum(shares)-1.0) > .001: errors.append("budget shares must sum to 1.0")
    if float(b.get("demand_gen_share",0)) != 0: errors.append("demand_gen_share must be 0 for the v1 template")
    ld=loc["lead_definition"]
    try: duration=int(ld.get("qualified_call_duration_seconds",0))
    except (TypeError,ValueError): duration=0
    if duration < 30: errors.append("qualified_call_duration_seconds must be at least 30")
    tr=loc["tracking"]
    for k in ("canonical_form_event","canonical_call_event","utm_template"):
        if not tr.get(k): errors.append(f"tracking.{k} is required")
    dep=loc["deployment"]
    if dep.get("mode") != "DRY_RUN": errors.append("deployment.mode must be DRY_RUN in the repository template")
    if dep.get("create_campaigns_paused") is not True: errors.append("deployment.create_campaigns_paused must be true")
    if dep.get("require_human_approval") is not True: errors.append("deployment.require_human_approval must be true")
    lsa=loc.get("lsa",{})
    if lsa.get("enabled") and not (lsa.get("eligible") and lsa.get("verified")): errors.append("LSA cannot be enabled until eligible and verified are true")
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("config"); args=ap.parse_args()
    try: data=yaml.safe_load(Path(args.config).read_text())
    except Exception as e: print(f"ERROR: cannot read YAML: {e}"); return 2
    errors=validate(data)
    if errors:
        print("INVALID LOCATION CONFIG")
        for e in errors: print(f"- {e}")
        return 1
    print("VALID LOCATION CONFIG")
    print(f"- slug: {data['location']['slug']}")
    print(f"- services enabled: {sum(1 for s in data['location']['services'] if s.get('enabled'))}")
    print("- deployment: DRY_RUN / paused campaigns / human approval required")
    return 0
if __name__=="__main__": sys.exit(main())
