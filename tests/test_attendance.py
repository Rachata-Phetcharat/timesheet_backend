import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_clock_in_success(client: AsyncClient, staff_headers: dict[str, str]):
    response = await client.post("/attendance/clock-in", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["clock_in_at"] is not None
    assert data["status"] in ["on_time", "late", "absent", "absent_half_morning", "absent_half_afternoon"]
    assert "id" in data


@pytest.mark.asyncio
async def test_clock_in_duplicate_same_day(client: AsyncClient, staff_headers: dict[str, str]):
    response1 = await client.post("/attendance/clock-in", headers=staff_headers)
    assert response1.status_code == 200

    response2 = await client.post("/attendance/clock-in", headers=staff_headers)
    assert response2.status_code == 400
    assert "Already clocked in today" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_clock_out_success(client: AsyncClient, staff_headers: dict[str, str]):
    # First clock in
    await client.post("/attendance/clock-in", headers=staff_headers)

    # Then clock out
    response = await client.post("/attendance/clock-out", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["clock_out_at"] is not None


@pytest.mark.asyncio
async def test_clock_out_without_clock_in(client: AsyncClient, staff_headers: dict[str, str]):
    response = await client.post("/attendance/clock-out", headers=staff_headers)
    assert response.status_code == 400
    assert "No clock-in record found for today" in response.json()["detail"]


@pytest.mark.asyncio
async def test_clock_out_duplicate(client: AsyncClient, staff_headers: dict[str, str]):
    await client.post("/attendance/clock-in", headers=staff_headers)
    await client.post("/attendance/clock-out", headers=staff_headers)

    response = await client.post("/attendance/clock-out", headers=staff_headers)
    assert response.status_code == 400
    assert "Already clocked out today" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_attendance_me(client: AsyncClient, staff_headers: dict[str, str]):
    await client.post("/attendance/clock-in", headers=staff_headers)

    response = await client.get("/attendance/me", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert "month" in data
    assert data["total_days"] == 1
    assert len(data["records"]) == 1


@pytest.mark.asyncio
async def test_get_attendance_with_month_filter(client: AsyncClient, staff_headers: dict[str, str]):
    response = await client.get("/attendance/me?month=2026-08", headers=staff_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == "2026-08"
