from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.leave_request import LeaveRequest, LeaveStatus, LeaveType


async def create_leave_request(
    db: AsyncSession,
    employee_id: str,
    leave_type: LeaveType,
    start_date: date,
    end_date: date,
    reason: str,
    duration: str = "full_day",
) -> LeaveRequest:
    leave_req = LeaveRequest(
        employee_id=employee_id,
        type=leave_type,
        duration=duration,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status=LeaveStatus.approved,
    )
    db.add(leave_req)
    await db.commit()
    await db.refresh(leave_req)
    return leave_req


async def get_leave_request_by_id(
    db: AsyncSession,
    leave_id: str,
) -> Optional[LeaveRequest]:
    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee))
        .where(LeaveRequest.id == leave_id)
    )
    return result.scalar_one_or_none()


async def get_leave_requests_by_employee(
    db: AsyncSession,
    employee_id: str,
) -> Sequence[LeaveRequest]:
    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee))
        .where(LeaveRequest.employee_id == employee_id)
        .order_by(LeaveRequest.start_date.desc())
    )
    return result.scalars().all()


async def get_all_leave_requests(
    db: AsyncSession,
) -> Sequence[LeaveRequest]:
    result = await db.execute(
        select(LeaveRequest)
        .options(selectinload(LeaveRequest.employee))
        .order_by(LeaveRequest.start_date.desc())
    )
    return result.scalars().all()


async def update_leave_status(
    db: AsyncSession,
    leave_request: LeaveRequest,
    status: LeaveStatus,
) -> LeaveRequest:
    leave_request.status = status
    await db.commit()
    await db.refresh(leave_request)
    return leave_request
