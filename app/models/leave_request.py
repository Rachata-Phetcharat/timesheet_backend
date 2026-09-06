from datetime import date
import enum
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class LeaveType(str, enum.Enum):
    personal = "personal"  # ลากิจ
    sick = "sick"          # ลาป่วย
    vacation = "vacation"  # ลาพักร้อน


class LeaveStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class LeaveDuration(str, enum.Enum):
    full_day = "full_day"
    morning = "morning"
    afternoon = "afternoon"

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    employee_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("employees.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    type: Mapped[LeaveType] = mapped_column(
        Enum(LeaveType, name="leave_type"),
        nullable=False,
    )
    duration: Mapped[LeaveDuration] = mapped_column(
        Enum(LeaveDuration, name="leave_duration"),
        nullable=False,
        default=LeaveDuration.full_day,
        server_default="full_day",
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[LeaveStatus] = mapped_column(
        Enum(LeaveStatus, name="leave_status"),
        default=LeaveStatus.pending,
        nullable=False,
    )

    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="leave_requests",
    )
