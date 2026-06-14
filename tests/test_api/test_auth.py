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
    ])
    def test_registration_password_issues(self, client: TestClient, password):
        registration_info = {
            "username": "CoolPerson53",
            "email": "validemail@validemail.com",
            "password": password
        }
        response = client.post("/auth/register", json=registration_info)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


