from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.attendance import AttendanceStatus


class AttendanceRecordResponse(BaseModel):
    id: str
    employee_id: str
    clock_in_at: Optional[datetime] = None
    clock_out_at: Optional[datetime] = None
    status: AttendanceStatus
    late_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceAdminRecordResponse(AttendanceRecordResponse):
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClockInResponse(BaseModel):
    id: str
    employee_id: str
    clock_in_at: Optional[datetime] = None
    clock_out_at: Optional[datetime] = None
    status: AttendanceStatus
    late_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ClockOutResponse(BaseModel):
    id: str
    employee_id: str
    clock_in_at: Optional[datetime] = None
    clock_out_at: Optional[datetime] = None
    status: AttendanceStatus
    late_minutes: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceMonthlySummary(BaseModel):
    month: str
    total_days: int
    on_time_count: int
    late_count: int
    absent_count: int
    total_late_minutes: int
    records: List[AttendanceRecordResponse]

    model_config = ConfigDict(from_attributes=True)
