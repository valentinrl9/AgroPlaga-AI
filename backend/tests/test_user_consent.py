from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.services.user_consent_service import ensure_map_consent


def test_ensure_map_consent_noop_when_already_set():
    db = MagicMock()
    user = MagicMock()
    user.consent_accepted_at = datetime.now(timezone.utc)

    ensure_map_consent(db, user)

    db.add.assert_not_called()
    db.flush.assert_not_called()


def test_ensure_map_consent_backfills_farmer():
    db = MagicMock()
    user = MagicMock()
    user.consent_accepted_at = None
    user.role = "farmer"

    ensure_map_consent(db, user)

    assert user.consent_accepted_at is not None
    db.add.assert_called_once_with(user)
    db.flush.assert_called_once()


def test_ensure_map_consent_rejects_non_farmer():
    db = MagicMock()
    user = MagicMock()
    user.consent_accepted_at = None
    user.role = "tech"

    with pytest.raises(ValueError, match="consentimiento"):
        ensure_map_consent(db, user)
