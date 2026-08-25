import asyncio
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_db
from app.core.database import Base
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.employee import Employee, EmployeeRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def staff_user(db_session: AsyncSession) -> Employee:
    user = Employee(
        id="staff-uuid-1234",
        email="staff@example.com",
        hashed_password=get_password_hash("staffpassword"),
        full_name="Staff Test User",
        role=EmployeeRole.staff,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> Employee:
    user = Employee(
        id="admin-uuid-5678",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin Test User",
        role=EmployeeRole.admin,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def staff_headers(staff_user: Employee) -> dict[str, str]:
    token = create_access_token(subject=staff_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_headers(admin_user: Employee) -> dict[str, str]:
    token = create_access_token(subject=admin_user.id)
    return {"Authorization": f"Bearer {token}"}
