from __future__ import annotations

from typing import List, Dict

import click


def parse_creator_strings(creator_person: List[str], creator_org: List[str]) -> List[Dict]:
    """Parse creator CLI strings into a structured list of dicts.

    Rules:
    - You may specify *either* personal or organizational creators in one
      command invocation, but not both. If both are provided, a click.UsageError
      is raised.
    - Each entry is a semicolon-separated string. The first segment is the
      display name; subsequent segments are optional key=value attributes, e.g.:

        "Doe, Jane; orcid=0000-0002-1825-0097; affiliation=Uni X"
        "Plato"
        "Org Name; ror=03yrm5c26"

    - Returned dicts are compatible with the Pydantic Creator model.
    - For Personal creators:
        - `family_name` is required. If not given as an attribute (e.g.,
          `family_name=...`), it's parsed from the display name. If the name is
          "Family, Given", both are extracted. Otherwise, the whole name is
          treated as the `family_name`.
        - `organization_name` attribute is not allowed.
    - For Organizational creators:
        - `organization_name` is required. If not given as an attribute, it
          defaults to the display name.
        - `family_name` and `given_name` attributes are not allowed.
    """
    if creator_person and creator_org:
        raise click.UsageError(
            "You cannot mix personal and organizational creators in a single "
            "command. Use either --creator-person or --creator-org, not both."
        )

    creators: List[Dict] = []
    is_personal = bool(creator_person)
    raw_strings = creator_person if is_personal else creator_org
    name_type = "Personal" if is_personal else "Organizational"

    for raw in raw_strings:
        parts = [p.strip() for p in raw.split(";") if p.strip()]
        if not parts:
            raise click.UsageError("Creator specification cannot be empty.")

        name = parts[0]
        creator_data: Dict[str, str] = {"name": name}

        # Parse key-value attributes
        for segment in parts[1:]:
            if "=" not in segment:
                raise click.UsageError(
                    f"Invalid creator attribute '{segment}'. Use key=value format."
                )
            key, value = [s.strip() for s in segment.split("=", 1)]
            if not key or not value:
                raise click.UsageError(
                    f"Invalid creator attribute '{segment}'. Key/value cannot be empty."
                )
            creator_data[key] = value

        # --- Apply Schema Logic ---
        creator_data["name_type"] = name_type

        if is_personal:
            if "organization_name" in creator_data:
                raise click.UsageError(
                    "The 'organization_name' attribute is not allowed for personal creators."
                )

            # Ensure family_name exists, deriving from `name` if not provided as an attribute.
            if "family_name" not in creator_data:
                if "," in name:
                    family, given = [p.strip() for p in name.split(",", 1)]
                    creator_data["family_name"] = family
                    if given and "given_name" not in creator_data:
                        creator_data["given_name"] = given
                else:
                    creator_data["family_name"] = name
        else:  # Organizational
            if "family_name" in creator_data or "given_name" in creator_data:
                raise click.UsageError(
                    "The 'family_name' or 'given_name' attributes are not allowed for organizational creators."
                )

            # Ensure organization_name exists, defaulting to the display name.
            if "organization_name" not in creator_data:
                creator_data["organization_name"] = name

        creators.append(creator_data)

    return creators
