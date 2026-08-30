import pytest, uuid
from fastapi import TestClient

from main import app


@pytest.fixture
def client():
    yield TestClient(app)


@pytest.fixture
def unique_user():
    fictional_user = "u_test" + uuid.uuid4().hex[:8]
    return {
        "username": fictional_user,
        "password": "12345",
        "email": f"{fictional_user}@t.dev",
    }
