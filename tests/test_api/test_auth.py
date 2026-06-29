from http import HTTPStatus

import pytest
from starlette.testclient import TestClient


class TestRegistration:

    def test_registration_success(self, client: TestClient):
        registration_info = {
            "username": "CoolPerson53",
            "email": "validemail@validemail.com",
            "password": "ThisisavalidPassword123!"
        }
        response = client.post("/auth/register", json=registration_info)

        assert response.status_code == HTTPStatus.CREATED


    def test_registration_username_already_taken(self, client: TestClient):
        registration_info = {
            "username": "TakenUsername",
            "email": "validemail@validemail.com",
            "password": "ThisisavalidPassword123!"
        }
        response = client.post("/auth/register", json=registration_info)
        assert response.status_code == HTTPStatus.CREATED

        registration_info["email"] = "differentemail@different.com"
        response = client.post("/auth/register", json=registration_info)
        assert response.status_code == HTTPStatus.CONFLICT

    def test_registration_username_too_long(self, client: TestClient):
        registration_info = {
            "username": "ThisUsernameIsFarTooLong",
            "email": "validemail@validemail.com",
            "password": "ThisisavalidPassword123!"
        }
        response = client.post("/auth/register", json=registration_info)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_registration_email_already_taken(self, client: TestClient):
        registration_info = {
            "username": "ValidUsername",
            "email": "takenemail@validemail.com",
            "password": "ThisisavalidPassword123!"
        }
        response = client.post("/auth/register", json=registration_info)
        assert response.status_code == HTTPStatus.CREATED

        registration_info["username"] = "DifferentName"
        response = client.post("/auth/register", json=registration_info)
        assert response.status_code == HTTPStatus.CONFLICT

    def test_registration_email_too_long(self, client: TestClient):
        registration_info = {
            "username": "ValidUsername",
            "email": "a" * 250 + "@b.com",
            "password": "ThisisavalidPassword123!"
        }
        response = client.post("/auth/register", json=registration_info)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("password", [
        "short1A!",  # too short
        "nouppercase1!",  # no uppercase
        "NOLOWERCASE1!",  # no lowercase
        "NoNumberHere!",  # no number
        "NoSymbol1234A",  # no symbol
        "Aa1!" + "a" * 252 # too long
    ])
    def test_registration_password_issues(self, client: TestClient, password):
        registration_info = {
            "username": "CoolPerson53",
            "email": "validemail@validemail.com",
            "password": password
        }
        response = client.post("/auth/register", json=registration_info)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

class TestAuth:
        def test_login(self, client: TestClient):
            registration_info = {
                "username": "CoolPerson53",
                "email": "validemail@validemail.com",
                "password": "ThisisavalidPassword123!"
            }
            response = client.post("/auth/register", json=registration_info)

            assert response.status_code == HTTPStatus.CREATED

            response = client.post("/auth/login", json=registration_info)
            assert response.status_code == HTTPStatus.OK
            assert "access_token" in response.json()
            assert "token_type" in response.json()

        def test_login_invalid_credentials(self, client: TestClient):
            response = client.post("/auth/login", json={"email": "randomemail10@email.com",
                                                        "password": "wrongpassword"})
            assert response.status_code == HTTPStatus.UNAUTHORIZED

        def test_get_current_user(self, client: TestClient):
            """
            Test that the current user can be retrieved and aa valid access token is present
            """
            registration_info = {
                "username": "CoolPerson53",
                "email": "validemail@validemail.com",
                "password": "ThisisavalidPassword123!"
            }
            response = client.post("/auth/register", json=registration_info)
            assert response.status_code == HTTPStatus.CREATED

            response = client.post("/auth/login", json={
                "email": registration_info["email"],
                "password": registration_info["password"]
            })
            assert response.status_code == HTTPStatus.OK
            token = response.json()["access_token"]

            response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == HTTPStatus.OK
            assert response.json()["email"] == "validemail@validemail.com"

        def test_get_current_user_invalid_token(self, client: TestClient):
            """An invalid token should be rejected."""
            response = client.get("/auth/me", headers={"Authorization": "Bearer not.a.valid.token"})
            assert response.status_code == HTTPStatus.UNAUTHORIZED

        def test_get_current_user_no_token(self, client: TestClient):
            """No Authorisation header at all should be rejected."""
            response = client.get("/auth/me")
            assert response.status_code == HTTPStatus.UNAUTHORIZED
