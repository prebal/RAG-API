from test_conf import client, unique_user, auth_headers


def get_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register_user(client, unique_user):
    response = client.post("/auth/register", json=unique_user)
    assert response.status_code == 200


def test_duplicate_registration(client, unique_user):
    response_first_registration = client.post("/auth/register", json=unique_user)
    response_second_registration = client.post("/auth/register", json=unique_user)
    assert response_first_registration.status_code == 200
    assert response_second_registration.status_code == 409
    assert response_second_registration.json() == {
        "detail": "User with this username already exists"
    }


def test_duplicate_registration_with_same_email(client, unique_user):
    response_first_registration = client.post("/auth/register", json=unique_user)
    response_second_registration_with_identical_email = client.post(
        "/auth/register",
        json={
            "username": unique_user["username"] + "1234",
            "password": unique_user["password"] + "1234",
            "email": unique_user["email"],
        },
    )
    assert response_first_registration.status_code == 200
    assert response_second_registration_with_identical_email.status_code == 409
    assert response_second_registration_with_identical_email.json() == {
        "detail": "User with this email already exists"
    }


def test_login_user(client, unique_user):
    client.post("/auth/register", json=unique_user)
    response = client.post("/auth/login", data=unique_user)
    assert response.status_code == 200


def test_login_user_bad_username(client, unique_user):
    client.post("/auth/register", json=unique_user)
    response = client.post(
        "/auth/login",
        data={**unique_user, "username": unique_user["username"] + "_changed"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect login or password"}


def test_login_user_bad_password(client, unique_user):
    client.post("/auth/register", json=unique_user)
    response = client.post(
        "/auth/login",
        data={**unique_user, "password": unique_user["password"] + "_changed"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect login or password"}


# -------Tests needing authentication--------
def test_me_users(client, auth_headers):
    response = client.get("/user/me", headers=auth_headers)
    assert response.status_code == 200


def test_change_username(client, unique_user, auth_headers):
    response = client.post(
        "/user/change_username",
        headers=auth_headers,
        json={
            "new_username": unique_user["username"] + "_renamed",
            "password": unique_user["password"],
        },
    )
    assert response.status_code == 200


def test_change_username_identical_username(client, unique_user, auth_headers):
    response = client.post(
        "/user/change_username",
        headers=auth_headers,
        json={
            "new_username": unique_user["username"],
            "password": unique_user["password"],
        },
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Old and new usernames are identical"}


def test_change_password(client, unique_user):
    client.post("/auth/register", json=unique_user)
    login_response = client.post("/auth/login", data=unique_user)

    tokens = login_response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    change_password_response = client.post(
        "/user/change_password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "old_password": unique_user["password"],
            "new_password": unique_user["password"] + "_changed",
        },
    )
    assert change_password_response.status_code == 200

    refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 401
    assert refresh_response.json() == {
        "detail": "Refresh token has already been revoked or is unknown"
    }


def test_change_password_identical_passwords(client, unique_user, auth_headers):
    response = client.post(
        "/user/change_password",
        headers=auth_headers,
        json={
            "old_password": unique_user["password"],
            "new_password": unique_user["password"],
        },
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Old and new passwords are identical"}
