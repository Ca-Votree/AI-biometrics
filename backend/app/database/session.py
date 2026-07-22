"""
Database Session Management
Quản lý kết nối database bằng SQLAlchemy async.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loguru import logger

from app.config import settings
from app.database.models import Base


# Tạo async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency injection cho FastAPI - tạo session mới cho mỗi request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Tạo tất cả bảng trong database (chạy 1 lần khi khởi động)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database đã được khởi tạo")


async def close_db():
    """Đóng kết nối database."""
    await engine.dispose()
    logger.info("Database connection đã được đóng")
