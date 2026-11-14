#!/usr/bin/env python3
"""Fail-closed QDesk authorization boundary for Delphi proposal work packets.

The QDesk caller must supply identities from its authenticated session and a
ledger_lookup backed by the canonical append-only Delphi ledger. This module
does not create work packets; callers must invoke require_work_packet_authorization
before any packet, campaign, design, or implementation dispatch is created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Callable

DELPHI_MODULES = str(Path(__file__).resolve().parents[1] / "delphi")
if DELPHI_MODULES not in sys.path:
    sys.path.insert(0, DELPHI_MODULES)

from proposal_package import verify_award, verify_files


class WorkPacketHeld(PermissionError):
    """Raised when proposal integrity or award authorization cannot be proven."""


def authorize_work_packet(
    *,
    manifest: dict,
    award: dict,
    package_root: str | Path,
    checkout_sha: str,
    authenticated_package_author: str,
    authenticated_reviewer: str,
    ledger_lookup: Callable[[str], dict | None] | None,
) -> dict:
    """Return AUTHORIZED only when package bytes, checkout, identities and ledger agree.

    Identity strings must be derived from QDesk's authenticated principal, never
    copied from the manifest, award, request body, or other caller-controlled data.
    The ledger callback must resolve the reference from the canonical signed
    Delphi ledger, not from an untrusted payload supplied with the work packet.
    """
    file_errors = verify_files(manifest, package_root, checkout_sha=checkout_sha)
    award_result = verify_award(
        manifest=manifest,
        award=award,
        package_author=authenticated_package_author,
        reviewer=authenticated_reviewer,
        ledger_lookup=ledger_lookup,
    )
    errors = file_errors + award_result["errors"]
    return {
        "schema": "qdesk-work-packet-authorization/v1",
        "disposition": "AUTHORIZED" if not errors else "HELD",
        "package_digest": manifest.get("package_digest") if isinstance(manifest, dict) else None,
        "reviewer_login": authenticated_reviewer if isinstance(authenticated_reviewer, str) else None,
        "errors": errors,
    }


def require_work_packet_authorization(**kwargs) -> dict:
    """Guard a QDesk packet-creation path; raise rather than permit a held request."""
    result = authorize_work_packet(**kwargs)
    if result["disposition"] != "AUTHORIZED":
        detail = "; ".join(result["errors"]) or "authorization could not be established"
        raise WorkPacketHeld(detail)
    return result
