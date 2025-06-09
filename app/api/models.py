"""
Модели базы данных: статьи и их краткие содержания.

- `Article`: статья с URL, заголовком, контентом и связями с родительскими и дочерними статьями.
- `Summary`: краткое содержание, связанное с конкретной статьёй.
- `article_links`: вспомогательная таблица для связи m2m между статьями (родитель-дочерняя).
"""



from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import Optional, List

from app.db.base import Base


article_links = Table(
    "article_links",
    Base.metadata,
    Column("parent_id", ForeignKey("articles.id"), primary_key=True),
    Column("child_id", ForeignKey("articles.id"), primary_key=True)
)


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    parents: Mapped[List["Article"]] = relationship(
        "Article",
        secondary=article_links,
        primaryjoin=id == article_links.c.child_id,
        secondaryjoin=id == article_links.c.parent_id,
        lazy="selectin",
        back_populates="children"
    )

    children: Mapped[List["Article"]] = relationship(
        "Article",
        secondary=article_links,
        primaryjoin=id == article_links.c.parent_id,
        secondaryjoin=id == article_links.c.child_id,
        lazy="selectin",
        back_populates="parents"
    )

    summary: Mapped[Optional["Summary"]] = relationship(
        back_populates="article", uselist=False, cascade="all, delete-orphan"
    )


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    article: Mapped["Article"] = relationship(back_populates="summary")
