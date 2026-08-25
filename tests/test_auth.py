import pytest
from httpx import AsyncClient
from app.core.security import create_refresh_token
from app.models.employee import Employee


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, staff_user: Employee):
    response = await client.post(
        "/auth/login",
        json={"email": "staff@example.com", "password": "staffpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, staff_user: Employee):
    response = await client.post(
        "/auth/login",
        json={"email": "staff@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, staff_user: Employee):
    refresh_token = create_refresh_token(subject=staff_user.id)
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid.jwt.token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, staff_headers: dict[str, str], staff_user: Employee):
    response = await client.get("/auth/me", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == staff_user.id
    assert data["email"] == staff_user.email
    assert data["role"] == "staff"
