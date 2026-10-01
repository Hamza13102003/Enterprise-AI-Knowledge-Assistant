from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an asynchronous database session for a request.
    """
    async with AsyncSessionLocal() as session:
        yield session
