import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


_ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset shared in-memory activity state before/after each test."""
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client