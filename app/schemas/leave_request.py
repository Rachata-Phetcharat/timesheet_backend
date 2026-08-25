from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator
from app.models.leave_request import LeaveStatus, LeaveType
from app.schemas.employee import EmployeeResponse


class LeaveRequestCreate(BaseModel):
    type: LeaveType
    start_date: date
    end_date: date
    reason: str

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class LeaveStatusUpdate(BaseModel):
    status: LeaveStatus


class LeaveRequestResponse(BaseModel):
    id: str
    employee_id: str
    type: LeaveType
    start_date: date
    end_date: date
    reason: str
    status: LeaveStatus
    employee: Optional[EmployeeResponse] = None

    model_config = ConfigDict(from_attributes=True)
