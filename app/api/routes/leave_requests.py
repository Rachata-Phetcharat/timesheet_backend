from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.employee import Employee
from app.schemas.leave_request import (
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveStatusUpdate,
)
from app.services.leave_service import (
    create_leave,
    get_leave_by_id,
    get_my_leaves,
    update_leave_status as service_update_leave_status,
)

router = APIRouter(prefix="/leave-requests", tags=["leave-requests"])


@router.get("/me", response_model=List[LeaveRequestResponse])
async def get_my_leave_requests(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return await get_my_leaves(db, employee_id=current_user.id)


@router.get("", response_model=List[LeaveRequestResponse])
async def get_all_leave_requests_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    from app.services.leave_service import get_all_leaves
    return await get_all_leaves(db)


@router.post("", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_request_endpoint(
    leave_in: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return await create_leave(db, employee_id=current_user.id, leave_in=leave_in)


@router.get("/{id}", response_model=LeaveRequestResponse)
async def get_leave_request_endpoint(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    return await get_leave_by_id(db, leave_id=id, current_user=current_user)


@router.patch("/{id}/status", response_model=LeaveRequestResponse)
async def update_leave_status_endpoint(
    id: str,
    status_update: LeaveStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: Employee = Depends(get_current_admin),
):
    from app.services.leave_service import update_leave_status as service_update_leave_status
    return await service_update_leave_status(
        db,
        leave_id=id,
        new_status=status_update.status,
        current_user=current_admin,
    )


@router.patch("/{id}/cancel", response_model=LeaveRequestResponse)
async def cancel_leave_request_endpoint(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user),
):
    from app.services.leave_service import cancel_leave_request as service_cancel
    return await service_cancel(
        db,
        leave_id=id,
        current_user=current_user,
    )
