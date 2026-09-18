"""Presentation helpers for anonymous browser identities."""

from uuid import UUID


def anonymous_label(user_id: UUID) -> str:
    """Return a short, non-sensitive display label for an anonymous identity."""

    return f"Viewer {user_id.hex[-6:].upper()}"
