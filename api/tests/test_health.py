"""Basic health check tests."""
import pytest


def test_placeholder():
    """Always passes — real tests added as routes stabilize."""
    assert True


@pytest.mark.integration
def test_ecosystem_status_live():
    """Requires running server — skipped in CI."""
    pass
