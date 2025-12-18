from __future__ import annotations

from typing import List, Dict

import click


def parse_creator_strings(creator_person: List[str], creator_org: List[str]) -> List[Dict]:
    """Parse creator CLI strings into a structured list of dicts.

    Rules:
    - You may specify *either* personal creators or organizational creators in one
      command invocation, but not both. If both are provided, a click.UsageError
      is raised.
    - Each entry is a semicolon-separated string. The first segment is the
      display name; subsequent segments are optional key=value attributes, e.g.:

        "Doe, Jane; orcid=0000-0002-1825-0097; affiliation=Uni X"
        "Org Name; ror=03yrm5c26; affiliation=Institute Y"

    - Returned dicts are DataCite-friendly and future-compatible with a Pydantic
      Creator model. Common keys:
        - type: "person" or "organization"
        - name: display name (DataCite creatorName)
        - given_name, family_name (optional, parsed from name if "Family, Given")
        - organization_name for organizations
        - orcid, affiliation, ror (optional extras)
    """
    if creator_person and creator_org:
        raise click.UsageError(
            "You cannot mix personal and organizational creators in a single "
            "command. Use either --creator-person or --creator-org, not both."
        )

    creators: List[Dict] = []

    def _parse_segments(raw: str) -> Dict:
        parts = [p.strip() for p in raw.split(";") if p.strip()]
        if not parts:
            raise click.UsageError("Creator specification cannot be empty.")

        # First part is the display name
        name = parts[0]
        data: Dict[str, str] = {"name": name}

        # Optionally split into family, given if formatted as "Family, Given"
        if "," in name:
            family, given = [p.strip() for p in name.split(",", 1)]
            if family:
                data["family_name"] = family
            if given:
                data["given_name"] = given

        for segment in parts[1:]:
            if "=" not in segment:
                raise click.UsageError(
                    f"Invalid creator attribute '{segment}'. Use key=value format."
                )
            key, value = [s.strip() for s in segment.split("=", 1)]
            if not key:
                raise click.UsageError(
                    f"Invalid creator attribute '{segment}'. Key cannot be empty."
                )
            if not value:
                raise click.UsageError(
                    f"Invalid creator attribute '{segment}'. Value cannot be empty."
                )
            data[key] = value

        return data

    if creator_person:
        for raw in creator_person:
            base = _parse_segments(raw)
            base["type"] = "person"
            creators.append(base)

    if creator_org:
        for raw in creator_org:
            base = _parse_segments(raw)
            base["type"] = "organization"
            if "organization_name" not in base:
                # Default organization_name to display name if not provided
                base["organization_name"] = base["name"]
            creators.append(base)

    return creators

