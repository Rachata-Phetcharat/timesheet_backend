from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.employee import Employee
from app.schemas.attendance import (
    AttendanceMonthlySummary,
    ClockInResponse,
    ClockOutResponse,
)
from app.services.attendance_service import (
    clock_in_employee,
    clock_out_employee,
    get_my_attendance,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("/me", response_model=AttendanceMonthlySummary)
async def get_my_monthly_attendance(
    month: Optional[str] = Query(
        None,
        description="Month in YYYY-MM format (e.g. 2026-08)",
        examples=["2026-08"],
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return await get_my_attendance(db, employee_id=current_user.id, month=month)


@router.post("/clock-in", response_model=ClockInResponse)
async def clock_in(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return await clock_in_employee(db, employee_id=current_user.id)


@router.post("/clock-out", response_model=ClockOutResponse)
async def clock_out(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return await clock_out_employee(db, employee_id=current_user.id)


from typing import List
from app.schemas.attendance import AttendanceAdminRecordResponse
from app.services.attendance_service import get_all_attendance_summary

@router.get("/all", response_model=List[AttendanceAdminRecordResponse])
async def get_all_monthly_attendance(
    month: Optional[str] = Query(
        None,
        description="Month in YYYY-MM format (e.g. 2026-08)",
        examples=["2026-08"],
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    # Depending on requirements, we might want to check if current_user.role == 'admin' here.
    return await get_all_attendance_summary(db, month=month)
