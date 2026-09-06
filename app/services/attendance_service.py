import calendar
from datetime import datetime, time
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.repositories.attendance_repo import (
    create_attendance_record,
    get_all_attendance_by_employee,
    get_attendance_records_by_range,
    get_today_attendance_record,
    update_attendance_clock_out,
)
from app.schemas.attendance import AttendanceMonthlySummary, AttendanceRecordResponse


def get_work_start_time() -> time:
    try:
        parts = settings.WORK_START_TIME.split(":")
        return time(int(parts[0]), int(parts[1]))
    except Exception:
        return time(9, 0)


async def clock_in_employee(
    db: AsyncSession,
    employee_id: str,
    clock_time: Optional[datetime] = None,
) -> AttendanceRecord:
    now = clock_time or datetime.now()
    start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)

    existing_record = await get_today_attendance_record(
        db, employee_id=employee_id, start_of_day=start_of_day, end_of_day=end_of_day
    )
    if existing_record and existing_record.clock_in_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already clocked in today",
        )

    current_minutes = now.hour * 60 + now.minute

    # Check for approved leaves today
    from sqlalchemy import select, and_
    from app.models.leave_request import LeaveRequest, LeaveStatus, LeaveDuration
    
    leave_query = select(LeaveRequest).where(
        and_(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.start_date <= now.date(),
            LeaveRequest.end_date >= now.date(),
            LeaveRequest.status == LeaveStatus.approved,
        )
    )
    result = await db.execute(leave_query)
    today_leave = result.scalars().first()

    if today_leave and today_leave.duration == LeaveDuration.full_day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot clock in: You are on full-day leave today",
        )

    if today_leave and today_leave.duration == LeaveDuration.morning:
        # ใช้เกณฑ์เข้างานบ่ายเท่านั้น
        if current_minutes <= 12 * 60 + 34: # ถึง 12:34
            att_status = AttendanceStatus.on_time
            late_minutes = 0
        elif current_minutes <= 13 * 60: # 12:35 - 13:00
            att_status = AttendanceStatus.late
            late_minutes = current_minutes - (12 * 60 + 30)
        else: # 13:01 เป็นต้นไป
            att_status = AttendanceStatus.absent_half_afternoon
            late_minutes = 0
    elif today_leave and today_leave.duration == LeaveDuration.afternoon:
        # ใช้เกณฑ์เข้างานเช้าเท่านั้น
        if current_minutes <= 9 * 60 + 4: # ถึง 09:04
            att_status = AttendanceStatus.on_time
            late_minutes = 0
        elif current_minutes <= 9 * 60 + 30: # 09:05 - 09:30
            att_status = AttendanceStatus.late
            late_minutes = current_minutes - (9 * 60)
        else: # 09:31 เป็นต้นไป
            att_status = AttendanceStatus.absent_half_morning
            late_minutes = 0
    else:
        # เกณฑ์ปกติ (ไม่มีลา หรือไม่ตรงกับลาครึ่งวัน)
        # เกณฑ์ช่วงเช้า
        if current_minutes <= 9 * 60 + 4: # ถึง 09:04
            att_status = AttendanceStatus.on_time
            late_minutes = 0
        elif current_minutes <= 9 * 60 + 30: # 09:05 - 09:30
            att_status = AttendanceStatus.late
            late_minutes = current_minutes - (9 * 60)
        elif current_minutes <= 12 * 60 + 29: # 09:31 - 12:29
            att_status = AttendanceStatus.absent_half_morning
            late_minutes = 0
        # เกณฑ์ช่วงบ่าย
        elif current_minutes <= 12 * 60 + 34: # 12:30 - 12:34
            att_status = AttendanceStatus.absent_half_morning # ขาดเช้า มาทันบ่าย
            late_minutes = 0
        elif current_minutes <= 13 * 60: # 12:35 - 13:00
            att_status = AttendanceStatus.absent_half_morning # ขาดเช้า มาสายบ่าย
            late_minutes = current_minutes - (12 * 60 + 30)
        else: # 13:01 เป็นต้นไป
            att_status = AttendanceStatus.absent_half_afternoon # ขาดบ่าย
            late_minutes = 0

    return await create_attendance_record(
        db=db,
        employee_id=employee_id,
        clock_in_at=now,
        status=att_status,
        late_minutes=late_minutes,
    )


async def clock_out_employee(
    db: AsyncSession,
    employee_id: str,
    clock_time: Optional[datetime] = None,
) -> AttendanceRecord:
    now = clock_time or datetime.now()
    start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
    end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)

    record = await get_today_attendance_record(
        db, employee_id=employee_id, start_of_day=start_of_day, end_of_day=end_of_day
    )
    if not record or record.clock_in_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clock-in record found for today",
        )

    if record.clock_out_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already clocked out today",
        )

    return await update_attendance_clock_out(db=db, record=record, clock_out_at=now)


async def get_my_attendance(
    db: AsyncSession,
    employee_id: str,
    month: Optional[str] = None,
) -> AttendanceMonthlySummary:
    now = datetime.now()
    if month:
        try:
            year_str, month_str = month.split("-")
            year = int(year_str)
            month_num = int(month_str)
            _, last_day = calendar.monthrange(year, month_num)
            start_time = datetime(year, month_num, 1, 0, 0, 0)
            end_time = datetime(year, month_num, last_day, 23, 59, 59)
            target_month = f"{year:04d}-{month_num:02d}"
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format. Expected YYYY-MM (e.g. 2026-08)",
            )
        records = await get_attendance_records_by_range(
            db, employee_id=employee_id, start_time=start_time, end_time=end_time
        )
    else:
        target_month = f"{now.year:04d}-{now.month:02d}"
        _, last_day = calendar.monthrange(now.year, now.month)
        start_time = datetime(now.year, now.month, 1, 0, 0, 0)
        end_time = datetime(now.year, now.month, last_day, 23, 59, 59)
        records = await get_attendance_records_by_range(
            db, employee_id=employee_id, start_time=start_time, end_time=end_time
        )

    on_time_count = sum(1 for r in records if r.status == AttendanceStatus.on_time)
    late_count = sum(1 for r in records if r.status == AttendanceStatus.late)
    absent_count = sum(1 for r in records if r.status == AttendanceStatus.absent)
    total_late_minutes = sum(r.late_minutes or 0 for r in records)

    return AttendanceMonthlySummary(
        month=target_month,
        total_days=len(records),
        on_time_count=on_time_count,
        late_count=late_count,
        absent_count=absent_count,
        total_late_minutes=total_late_minutes,
        records=[AttendanceRecordResponse.model_validate(r) for r in records],
    )


async def get_all_attendance_summary(
    db: AsyncSession,
    month: Optional[str] = None,
):
    now = datetime.now()
    if month:
        try:
            year_str, month_str = month.split("-")
            year = int(year_str)
            month_num = int(month_str)
            _, last_day = calendar.monthrange(year, month_num)
            start_time = datetime(year, month_num, 1, 0, 0, 0)
            end_time = datetime(year, month_num, last_day, 23, 59, 59)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid month format. Expected YYYY-MM (e.g. 2026-08)",
            )
    else:
        _, last_day = calendar.monthrange(now.year, now.month)
        start_time = datetime(now.year, now.month, 1, 0, 0, 0)
        end_time = datetime(now.year, now.month, last_day, 23, 59, 59)

    from app.repositories.attendance_repo import get_all_employees_attendance_records
    records = await get_all_employees_attendance_records(
        db, start_time=start_time, end_time=end_time
    )

    from app.schemas.attendance import AttendanceAdminRecordResponse
    response_records = []
    for r in records:
        resp = AttendanceAdminRecordResponse.model_validate(r)
        if r.employee:
            resp.employee_name = r.employee.full_name
            resp.employee_email = r.employee.email
        response_records.append(resp)

    return response_records
