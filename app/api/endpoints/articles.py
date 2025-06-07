from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.deps import SessionDep
from app.api.schemas import UrlSchema
from app.api.services import ArticleParserService, fetch_ai_summary
from app.api.crud import DB

router = APIRouter()



@router.post("/parse", summary='Parse articles')
async def parse_article(url_schema: UrlSchema, session: SessionDep):
    db = DB(session)
    existing_article = await db.get_by_url(str(url_schema.url))
    if not existing_article:
        parse_service = ArticleParserService(url_schema, db)
        await parse_service.parse()
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={'success': True, 'article_url': str(url_schema.url)}
        )
    return JSONResponse(
    status_code=status.HTTP_409_CONFLICT,
    content={'error': 'Article with this URL already exists'}
)


@router.post("/summary", summary='Get articles summary')
async def get_summary(url_schema: UrlSchema, session: SessionDep):
    db = DB(session)
    existing_article = await db.get_by_url(str(url_schema.url))
    if existing_article:
        return {"summary": existing_article.summary.content}
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'error': 'Article with this URL not found'}
    )
