from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.employee import Employee, EmployeeRole
from app.models.leave_request import LeaveRequest, LeaveStatus
from app.repositories.leave_repo import (
    create_leave_request,
    get_all_leave_requests,
    get_leave_request_by_id,
    get_leave_requests_by_employee,
    update_leave_status as repo_update_leave_status,
)
from app.schemas.leave_request import LeaveRequestCreate


async def create_leave(
    db: AsyncSession,
    employee_id: str,
    leave_in: LeaveRequestCreate,
) -> LeaveRequest:
    if leave_in.end_date < leave_in.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be on or after start_date",
        )
    return await create_leave_request(
        db=db,
        employee_id=employee_id,
        leave_type=leave_in.type,
        start_date=leave_in.start_date,
        end_date=leave_in.end_date,
        reason=leave_in.reason,
        duration=leave_in.duration,
    )


async def get_my_leaves(
    db: AsyncSession,
    employee_id: str,
) -> Sequence[LeaveRequest]:
    return await get_leave_requests_by_employee(db=db, employee_id=employee_id)


async def get_all_leaves(
    db: AsyncSession,
) -> Sequence[LeaveRequest]:
    return await get_all_leave_requests(db=db)


async def get_leave_by_id(
    db: AsyncSession,
    leave_id: str,
    current_user: Employee,
) -> LeaveRequest:
    leave_req = await get_leave_request_by_id(db=db, leave_id=leave_id)
    if not leave_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    if current_user.role != EmployeeRole.admin and leave_req.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this leave request",
        )
    return leave_req


async def update_leave_status(
    db: AsyncSession,
    leave_id: str,
    new_status: LeaveStatus,
    current_user: Employee,
) -> LeaveRequest:
    if current_user.role != EmployeeRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to update leave request status",
        )
    leave_req = await get_leave_request_by_id(db=db, leave_id=leave_id)
    if not leave_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    return await repo_update_leave_status(
        db=db,
        leave_request=leave_req,
        status=new_status,
    )


async def cancel_leave_request(
    db: AsyncSession,
    leave_id: str,
    current_user: Employee,
) -> LeaveRequest:
    leave_req = await get_leave_request_by_id(db=db, leave_id=leave_id)
    if not leave_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found",
        )
    if leave_req.employee_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own leave requests",
        )
    if leave_req.status not in (LeaveStatus.pending, LeaveStatus.approved):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending or approved leave requests can be cancelled",
        )
    return await repo_update_leave_status(
        db=db,
        leave_request=leave_req,
        status=LeaveStatus.cancelled,
    )
