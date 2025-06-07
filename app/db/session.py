from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

env = os.getenv("ENV", "local")
DATABASE_URL = os.getenv("DATABASE_URL_LOCAL") if env == "local" else os.getenv("DATABASE_URL_DOCKER")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
