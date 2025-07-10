from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

engine = create_async_engine(settings.DB_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()