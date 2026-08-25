from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.employee import Employee, EmployeeRole


async def get_employee_by_id(db: AsyncSession, employee_id: str) -> Optional[Employee]:
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    return result.scalar_one_or_none()


async def get_employee_by_email(db: AsyncSession, email: str) -> Optional[Employee]:
    result = await db.execute(select(Employee).where(Employee.email == email))
    return result.scalar_one_or_none()


async def create_employee(
    db: AsyncSession,
    email: str,
    hashed_password: str,
    full_name: str,
    role: EmployeeRole = EmployeeRole.staff,
) -> Employee:
    employee = Employee(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        role=role,
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee


async def get_all_employees(db: AsyncSession) -> Sequence[Employee]:
    result = await db.execute(select(Employee).order_by(Employee.full_name))
    return result.scalars().all()
