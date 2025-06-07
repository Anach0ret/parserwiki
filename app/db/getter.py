from app.db.session import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager



async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
