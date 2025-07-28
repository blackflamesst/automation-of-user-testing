import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from app.database.models import Base
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session_fixture():
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestSessionLocal = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
        expire_on_commit=False
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_context_manager = TestSessionLocal()
    session = await session_context_manager.__aenter__()

    try:
        yield session
    finally:
        await session_context_manager.__aexit__(None, None, None)
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()

@pytest.fixture
async def bot():
    mock_bot = AsyncMock(spec=Bot)
    yield mock_bot

@pytest.fixture
async def dp():
    storage = MemoryStorage()
    mock_dp = Dispatcher(storage=storage)
    yield mock_dp
    await storage.close()

@pytest.fixture
def state(dp):
    return dp.fsm.get_context(bot=AsyncMock(), chat_id=123, user_id=123)

@pytest.fixture(autouse=True)
def override_db_session_factory(db_session_fixture):
    mock_context_manager_instance = MagicMock()
    mock_context_manager_instance.__aenter__ = AsyncMock(return_value=db_session_fixture)
    mock_context_manager_instance.__aexit__ = AsyncMock(return_value=None)
    mock_async_session_factory = MagicMock(return_value=mock_context_manager_instance)

    with patch('app.database.models.async_session', new=mock_async_session_factory), \
         patch('app.database.requests.async_session', new=mock_async_session_factory):
        yield