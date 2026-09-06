import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.employee import Employee, EmployeeRole
from app.repositories.employee_repo import get_employee_by_email


async def seed():
    async with AsyncSessionLocal() as db:
        admin_email = "admin@timesheet.com"
        staff_email = "staff@timesheet.com"

        admin = await get_employee_by_email(db, admin_email)
        if not admin:
            admin = Employee(
                email=admin_email,
                hashed_password=get_password_hash("admin1234"),
                full_name="System Admin",
                role=EmployeeRole.admin,
            )
            db.add(admin)
            print(f"Created default admin user: {admin_email} / admin1234")

        staff = await get_employee_by_email(db, staff_email)
        if not staff:
            staff = Employee(
                email=staff_email,
                hashed_password=get_password_hash("staff1234"),
                full_name="Staff Employee",
                role=EmployeeRole.staff,
            )
            db.add(staff)
            print(f"Created default staff user: {staff_email} / staff1234")

        newuser_email = "newuser@timesheet.com"
        newuser = await get_employee_by_email(db, newuser_email)
        if not newuser:
            newuser = Employee(
                email=newuser_email,
                hashed_password=get_password_hash("newuser1234"),
                full_name="New Employee",
                role=EmployeeRole.staff,
            )
            db.add(newuser)
            print(f"Created new user: {newuser_email} / newuser1234")

        await db.commit()
        print("Database seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
