from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.endpoints.articles import router as article_router
from app.db.session import engine
from app.api.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(article_router, prefix="/articles", tags=["Wiki articles"])


