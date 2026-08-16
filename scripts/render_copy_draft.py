#!/usr/bin/env python3
"""Render review-only RSA copy drafts from an approved location config."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from validate_location import validate


HEADLINE_LIMIT = 30
DESCRIPTION_LIMIT = 90


def clean(value: object) -> str:
    """Normalize a configured or generated copy value without changing its meaning."""
    return re.sub(r"\s+", " ", str(value)).strip()


def unique_fit(candidates: list[str], used: set[str], limit: int) -> str | None:
    """Return the first unique candidate that fits the Google Ads character limit."""
    for candidate in candidates:
        text = clean(candidate)
        key = text.casefold()
        if text and len(text) <= limit and key not in used:
            used.add(key)
            return text
    return None


def configured_variants(location: dict[str, object], limit: int) -> list[tuple[str, str, str]]:
    """Return configured offer/claim variants with their source field and fit status."""
    claims = location.get("claims", {}) or {}
    variants: list[tuple[str, str, str]] = []
    for field, label in (
        ("approved_offers", "approved offer"),
        ("approved_guarantees", "approved guarantee"),
        ("approved_review_claims", "approved review claim"),
    ):
        for value in claims.get(field, []) or []:
            text = clean(value)
            status = "fits limit" if len(text) <= limit else f"over {limit}-character limit"
            variants.append((label, text, status))
    return variants


def headline_candidates(location: dict[str, object], service: dict[str, object]) -> list[str]:
    """Build neutral, location-specific headline candidates.

    Configured claims/offers are added separately and only used when they fit the
    limit. The core candidates intentionally avoid prices, guarantees, review
    counts, and other facts that are not present in the location config.
    """
    brand = clean(location["brand_name"])
    city = clean(location["city"])
    name = clean(service["name"])
    return [
        f"{name} in {city}",
        f"{name} Near You",
        f"Local {name}",
        f"{brand} in {city}",
        f"Book {name}",
        f"Schedule {name}",
        "Request a Quote",
        "Get a Quote",
        "Choose a Service Time",
        "Online Booking",
        f"Call {brand}",
        "Local Service Options",
        "Service Options",
        "Request Service Today",
        "Book Online Today",
        "Get Started Today",
        f"{name} Services",
        "Cleaning Services Near You",
        "Plan Your Service",
        "Start With a Quote",
        "Book a Local Service",
        "Explore Service Options",
    ]


def render_headlines(
    location: dict[str, object], service: dict[str, object]
) -> tuple[list[tuple[str, str]], list[tuple[str, str, str]]]:
    """Return 15 complete headlines and configured variants not used in the set."""
    used: set[str] = set()
    headlines: list[tuple[str, str]] = []
    candidates = headline_candidates(location, service)
    core_count = 12

    for candidate in candidates:
        if len(headlines) >= core_count:
            break
        text = unique_fit([candidate], used, HEADLINE_LIMIT)
        if text:
            headlines.append((text, "generated from service/location fields"))

    variants = configured_variants(location, HEADLINE_LIMIT)
    for label, text, status in variants:
        if len(headlines) >= 15:
            break
        if status == "fits limit":
            fitted = unique_fit([text], used, HEADLINE_LIMIT)
            if fitted:
                headlines.append((fitted, f"configured {label}"))

    for candidate in candidates:
        if len(headlines) >= 15:
            break
        text = unique_fit([candidate], used, HEADLINE_LIMIT)
        if text:
            headlines.append((text, "generated fallback"))

    # These static fallbacks leave enough room for unusually long brand/service names.
    for candidate in (
        "Request Service",
        "Book Today",
        "Get Started",
        "Local Service",
        "Service Near You",
        "Request Information",
        "Schedule Online",
        "Call for Details",
    ):
        if len(headlines) >= 15:
            break
        text = unique_fit([candidate], used, HEADLINE_LIMIT)
        if text:
            headlines.append((text, "generated fallback"))

    if len(headlines) != 15:
        raise ValueError("could not produce 15 unique headlines within the 30-character limit")

    used_variant_keys = {text.casefold() for text, _ in headlines}
    unused_variants = [
        (label, text, status)
        for label, text, status in variants
        if text.casefold() not in used_variant_keys
    ]
    return headlines, unused_variants


def description_candidates(location: dict[str, object], service: dict[str, object]) -> list[tuple[str, str]]:
    """Build four descriptions, using configured offers only when they fit."""
    brand = clean(location["brand_name"])
    city = clean(location["city"])
    name = clean(service["name"])
    claims = location.get("claims", {}) or {}
    candidates: list[tuple[str, str]] = [
        (
            f"{name} in {city}. Request a quote online.",
            "generated from service/location fields",
        ),
        (
            f"Book {name.lower()} in {city}. Call or request a quote.",
            "generated from service/location fields",
        ),
        (
            f"Review {name.lower()} options and choose a service time.",
            "generated from service/location fields",
        ),
        (
            f"Visit {brand} online for service details.",
            "generated from brand/location fields",
        ),
    ]

    for value in claims.get("approved_offers", []) or []:
        text = clean(value)
        candidates.insert(
            1,
            (
                f"{text} See service details and request a quote from {brand}.",
                "configured approved offer",
            ),
        )
    for value in claims.get("approved_guarantees", []) or []:
        text = clean(value)
        candidates.insert(
            1,
            (
                f"{text} Review {name.lower()} details and request a quote from {brand}.",
                "configured approved guarantee",
            ),
        )

    candidates.append(
        (
            f"Request a quote for {name.lower()}.",
            "generated fallback",
        )
    )
    candidates.extend(
        [
            (f"Book {name.lower()} online.", "generated fallback"),
            (f"Service options in {city}.", "generated fallback"),
            ("Request a quote online today.", "generated fallback"),
            ("Local service. Choose a time that works for you.", "generated fallback"),
            ("Call or book online today.", "generated fallback"),
        ]
    )
    return candidates


def render_descriptions(
    location: dict[str, object], service: dict[str, object]
) -> list[tuple[str, str]]:
    """Return four unique descriptions within the 90-character limit."""
    used: set[str] = set()
    descriptions: list[tuple[str, str]] = []
    for candidate, source in description_candidates(location, service):
        text = unique_fit([candidate], used, DESCRIPTION_LIMIT)
        if text:
            descriptions.append((text, source))
        if len(descriptions) == 4:
            break
    if len(descriptions) != 4:
        raise ValueError("could not produce 4 unique descriptions within the 90-character limit")
    return descriptions


def checkbox(label: str) -> str:
    return f"- [ ] {label}"


def render(location: dict[str, object], config_path: Path) -> str:
    enabled_services = [s for s in location["services"] if s.get("enabled")]
    lines = [
        f"# RSA copy draft — {clean(location['brand_name'])} / {clean(location['city'])}, "
        f"{clean(location['state'])}",
        "",
        "**Status:** DRAFT ONLY · human review and explicit approval required · not deployed",
        f"**Generated from:** `{config_path.name}`",
        "",
        "This worksheet turns the validated location config into a complete Responsive "
        "Search Ad draft for each enabled service. It is a starting point for review, "
        "not a policy approval or live Google Ads change.",
        "",
        "## Global copy guardrails",
        "",
        "- Headlines are kept at or below 30 characters; descriptions are kept at or below 90.",
        "- Core copy uses only the configured brand, city, service name, landing page, and booking/quote language.",
        "- Prices, guarantees, review counts, response-time promises, and offers are not invented.",
        "- Configured offers or claims are included only when they fit the character limit; "
        "the owner must still verify substantiation and policy eligibility.",
        "- Review every line for accuracy, local serviceability, trademark/policy risk, and landing-page alignment.",
        "",
        "## Location inputs used",
        "",
        f"- Brand: `{clean(location['brand_name'])}`",
        f"- City/state: `{clean(location['city'])}, {clean(location['state'])}`",
        f"- Enabled services: {len(enabled_services)}",
        f"- Form event: `{clean(location['tracking']['canonical_form_event'])}`",
        f"- Call event: `{clean(location['tracking']['canonical_call_event'])}`",
        "",
        "The copy draft does not change conversion settings. Keep campaigns paused until "
        "the measurement gate and exact deployment diff are approved.",
        "",
    ]

    for index, service in enumerate(enabled_services, start=1):
        headlines, unused_variants = render_headlines(location, service)
        descriptions = render_descriptions(location, service)
        keywords = [clean(k) for k in service.get("keywords", [])]
        lines.extend(
            [
                f"## {index}. {clean(service['name'])}",
                "",
                f"- Ad group: `{clean(service['ad_group'])}`",
                f"- Final URL: `{clean(service['landing_page'])}`",
                f"- Keyword seeds: {', '.join(f'`{k}`' for k in keywords)}",
                "",
                "### Headlines",
                "",
                "| # | Draft | Characters | Source |",
                "|---:|---|---:|---|",
            ]
        )
        for slot, (text, source) in enumerate(headlines, start=1):
            lines.append(f"| {slot} | {text} | {len(text)} | {source} |")
        lines.extend(
            [
                "",
                "### Descriptions",
                "",
                "| # | Draft | Characters | Source |",
                "|---:|---|---:|---|",
            ]
        )
        for slot, (text, source) in enumerate(descriptions, start=1):
            lines.append(f"| {slot} | {text} | {len(text)} | {source} |")
        lines.extend(
            [
                "",
                "### Configured variants not used in the four-by-15 draft",
                "",
            ]
        )
        if unused_variants:
            lines.extend(
                [
                    "| Type | Text | Status |",
                    "|---|---|---|",
                ]
            )
            for label, text, status in unused_variants:
                lines.append(f"| {label} | {text} | {status} |")
        else:
            lines.append("No additional configured offer or claim variants.")
        lines.extend(
            [
                "",
                "### Service review checklist",
                "",
                checkbox("The service is sold, staffed, and available in the configured area."),
                checkbox("The final URL is the correct page for this service and location."),
                checkbox("Every keyword seed matches the service intent and page content."),
                checkbox("Every headline and description is accurate and policy-safe."),
                checkbox("Any configured offer/guarantee/review claim is substantiated and approved."),
                checkbox("The human approver accepts this exact copy before deployment."),
                "",
            ]
        )

    lines.extend(
        [
            "## Final approval checklist",
            "",
            checkbox("Location owner reviewed all service drafts."),
            checkbox("Landing pages, phone handling, hours, and offers match the draft."),
            checkbox("Measurement QA passed: canonical form, qualified call, and CRM receipt."),
            checkbox("The exact Google Ads diff includes these headlines, descriptions, and URLs."),
            checkbox("Campaigns remain paused until explicit approval is recorded."),
            "",
            "Approver: `[ ]`  ",
            "Approval timestamp: `[ ]`  ",
            "Destination account: `[NEVER COMMIT — supply through the connected integration]`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a review-only RSA copy draft from a validated location YAML."
    )
    parser.add_argument("config", help="Location YAML path")
    parser.add_argument("--out", required=True, help="Private Markdown output path")
    args = parser.parse_args()

    config_path = Path(args.config)
    try:
        data = yaml.safe_load(config_path.read_text())
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"ERROR: cannot read YAML: {exc}", file=sys.stderr)
        return 2

    errors = validate(data)
    if errors:
        print("Refusing to render copy for invalid config:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    try:
        output = render(data["location"], config_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output + "\n")
    print(f"WROTE {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
