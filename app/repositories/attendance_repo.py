from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.attendance import AttendanceRecord, AttendanceStatus


async def create_attendance_record(
    db: AsyncSession,
    employee_id: str,
    clock_in_at: Optional[datetime],
    status: AttendanceStatus,
    late_minutes: Optional[int] = None,
) -> AttendanceRecord:
    record = AttendanceRecord(
        employee_id=employee_id,
        clock_in_at=clock_in_at,
        status=status,
        late_minutes=late_minutes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def get_attendance_by_id(
    db: AsyncSession,
    record_id: str,
) -> Optional[AttendanceRecord]:
    result = await db.execute(select(AttendanceRecord).where(AttendanceRecord.id == record_id))
    return result.scalar_one_or_none()


async def get_today_attendance_record(
    db: AsyncSession,
    employee_id: str,
    start_of_day: datetime,
    end_of_day: datetime,
) -> Optional[AttendanceRecord]:
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.clock_in_at >= start_of_day,
                AttendanceRecord.clock_in_at <= end_of_day,
            )
        )
        .order_by(AttendanceRecord.clock_in_at.desc())
    )
    return result.scalars().first()


async def get_attendance_records_by_range(
    db: AsyncSession,
    employee_id: str,
    start_time: datetime,
    end_time: datetime,
) -> Sequence[AttendanceRecord]:
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.clock_in_at >= start_time,
                AttendanceRecord.clock_in_at <= end_time,
            )
        )
        .order_by(AttendanceRecord.clock_in_at.asc())
    )
    return result.scalars().all()


async def get_all_attendance_by_employee(
    db: AsyncSession,
    employee_id: str,
) -> Sequence[AttendanceRecord]:
    result = await db.execute(
        select(AttendanceRecord)
        .where(AttendanceRecord.employee_id == employee_id)
        .order_by(AttendanceRecord.clock_in_at.desc())
    )
    return result.scalars().all()


async def update_attendance_clock_out(
    db: AsyncSession,
    record: AttendanceRecord,
    clock_out_at: datetime,
) -> AttendanceRecord:
    record.clock_out_at = clock_out_at
    await db.commit()
    await db.refresh(record)
    return record
