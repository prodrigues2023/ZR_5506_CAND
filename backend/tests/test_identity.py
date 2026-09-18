from uuid import UUID

from app.presentation.identity import anonymous_label


def test_anonymous_label_is_stable_and_does_not_expose_full_uuid() -> None:
    user_id = UUID("12345678-1234-5678-1234-123456abcdef")

    assert anonymous_label(user_id) == "Viewer ABCDEF"
    assert str(user_id) not in anonymous_label(user_id)
