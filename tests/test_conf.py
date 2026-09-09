import pytest, uuid
from fastapi.testclient import TestClient

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


@pytest.fixture
def auth_headers(client, unique_user):
    client.post("/auth/register", json=unique_user)
    tokens = client.post("/auth/login", data=unique_user).json()

    return {"Authorization": f"Bearer {tokens['access_token']}"}
