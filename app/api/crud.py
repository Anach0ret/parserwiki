from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models import Article, Summary
from app.deps import SessionDep


class DB:
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_by_url(self, url: str) -> Article | None:
        result = await self.session.execute(
            select(Article)
            .where(Article.url == url)
            .options(selectinload(Article.summary))
        )
        return result.scalars().first()

    async def create_get_article(self, data: dict, parent: Article=None) -> Article:
        article = await self.get_by_url(data["url"])
        if not article:
            article = Article(
                url=data["url"],
                title=data["title"],
                content=data["content"],
            )
        if parent:
            article.parents.append(parent)
        self.session.add(article)
        return article

    async def create_summary(self, content: str, article_id: int=None):
        summary = Summary(content=content, article_id=article_id)
        self.session.add(summary)
