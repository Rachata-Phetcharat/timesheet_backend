import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_leave_request_success(client: AsyncClient, staff_headers: dict[str, str]):
    response = await client.post(
        "/leave-requests",
        headers=staff_headers,
        json={
            "type": "sick",
            "start_date": "2026-08-26",
            "end_date": "2026-08-27",
            "reason": "Doctor appointment",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "sick"
    assert data["status"] == "pending"
    assert data["start_date"] == "2026-08-26"
    assert data["end_date"] == "2026-08-27"
    assert data["reason"] == "Doctor appointment"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_leave_request_invalid_date_range(
    client: AsyncClient, staff_headers: dict[str, str]
):
    response = await client.post(
        "/leave-requests",
        headers=staff_headers,
        json={
            "type": "personal",
            "start_date": "2026-08-28",
            "end_date": "2026-08-26",
            "reason": "Vacation",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_my_leave_requests(client: AsyncClient, staff_headers: dict[str, str]):
    # Create a leave request
    await client.post(
        "/leave-requests",
        headers=staff_headers,
        json={
            "type": "personal",
            "start_date": "2026-08-26",
            "end_date": "2026-08-26",
            "reason": "Personal errands",
        },
    )

    response = await client.get("/leave-requests/me", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["type"] == "personal"


@pytest.mark.asyncio
async def test_get_leave_request_by_id(
    client: AsyncClient,
    staff_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    create_resp = await client.post(
        "/leave-requests",
        headers=staff_headers,
        json={
            "type": "sick",
            "start_date": "2026-08-26",
            "end_date": "2026-08-26",
            "reason": "Headache",
        },
    )
    leave_id = create_resp.json()["id"]

    # Staff can view own leave request
    resp_staff = await client.get(f"/leave-requests/{leave_id}", headers=staff_headers)
    assert resp_staff.status_code == 200
    assert resp_staff.json()["id"] == leave_id

    # Admin can view staff's leave request
    resp_admin = await client.get(f"/leave-requests/{leave_id}", headers=admin_headers)
    assert resp_admin.status_code == 200
    assert resp_admin.json()["id"] == leave_id


@pytest.mark.asyncio
async def test_update_leave_status_as_staff_forbidden(
    client: AsyncClient, staff_headers: dict[str, str]
):
    create_resp = await client.post(
        "/leave-requests",
        headers=staff_headers,
        json={
            "type": "sick",
            "start_date": "2026-08-26",
            "end_date": "2026-08-26",
            "reason": "Fever",
        },
    )
    leave_id = create_resp.json()["id"]

    # Staff attempts to approve own leave
    patch_resp = await client.patch(
        f"/leave-requests/{leave_id}/status",
        headers=staff_headers,
        json={"status": "approved"},
    )
    assert patch_resp.status_code == 403


@pytest.mark.asyncio
async def test_update_leave_status_as_admin_success(
    client: AsyncClient,
    staff_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    create_resp = await client.post(
        "/leave-requests",
        headers=staff_headers,
        json={
            "type": "sick",
            "start_date": "2026-08-26",
            "end_date": "2026-08-26",
            "reason": "Doctor checkup",
        },
    )
    leave_id = create_resp.json()["id"]

    # Admin approves leave
    patch_resp = await client.patch(
        f"/leave-requests/{leave_id}/status",
        headers=admin_headers,
        json={"status": "approved"},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["id"] == leave_id
    assert data["status"] == "approved"
