import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.db.database import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope='function')
async def session():
	"""
	Фикстура, которая создаёт чистую БД в памяти для каждого теста.
	"""
	engine = create_async_engine(TEST_DB_URL)

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	TestSessionLocal = async_sessionmaker(autoflush=False, bind=engine, expire_on_commit=False)
	async with TestSessionLocal() as session:
		yield session

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)

	await engine.dispose()