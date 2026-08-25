from pydantic import BaseModel, ConfigDict, EmailStr
from app.models.employee import EmployeeRole


class EmployeeBase(BaseModel):
    email: EmailStr
    full_name: str
    role: EmployeeRole = EmployeeRole.staff


class EmployeeCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: EmployeeRole = EmployeeRole.staff


class EmployeeResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: EmployeeRole

    model_config = ConfigDict(from_attributes=True)
