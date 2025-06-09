"""
Сервис для парсинга и генерации краткого содержания статьи.

- `ArticleParserService`: парсит родительскую статью, асинхронно обрабатывает дочерние ссылки.
- Использует `Parser` для извлечения данных и `DB` для работы с БД.
- Генерирует summary через внешнюю AI-модель (OpenRouter).
"""


import aiohttp
import asyncio
from dotenv import load_dotenv
import os

from app.api.schemas import UrlSchema
from app.api.crud import DB
from app.api.models import Article
from app.api.utils import Parser

load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY")

async def fetch_ai_summary(content: str):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sentientagi/dobby-mini-unhinged-plus-llama-3.1-8b",
        "max_tokens": 1400,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes articles clearly and briefly."},
            {"role": "user", "content": f"Summarize the following article in 5-6 sentences:\n\n{content}"}
        ]
    }

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, json=payload, headers=headers, ssl=False) as response:
            if response.status != 200:
                text = await response.text()
                print(f"OpenAi API error: {response.status} - {text}")

            data = await response.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise ValueError(f"Unexpected AI response: {data}") from e


async def fetch(url: str):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, ssl=False) as response:
            if response.status == 200:
                return await response.text()
            else:
                return False



class ArticleParserService:
    def __init__(self,db: DB):
        self.db = db

        self.tasks = []


    async def parse(self, url: UrlSchema):
        url = str(url.url)
        html_page = await fetch(url)

        if not html_page:
            return {"error": "Failed to fetch parent article"}

        parser = Parser(parent=True, url=url, html=html_page)
        parser.parse()
        db_article = await self.db.create_get_article(data=parser.generate_data_dict())
        await self.db.flush_session()
        self.tasks.append(self.generate_summary(db_article))
        self.tasks.extend([self._parse_child(url) for url in parser.urls])

        children = await self._execute_tasks()
        await self._create_child(children, db_article)

        return True


    async def _execute_tasks(self):
        return await asyncio.gather(*self.tasks, return_exceptions=False)

    async def _parse_child(self, url: str):
        html_page = await fetch(url)
        if not html_page:
            return None
        parser = Parser(parent=False, url=url, html=html_page)
        parser.parse()
        return parser.generate_data_dict()

    async def _create_child(self, children_data: list[dict], parent: Article):
        for child_data in children_data:
            if child_data is None:
                continue
            await self.db.create_get_article(data=child_data, parent=parent)

    async def generate_summary(self, article: Article):
        summary = await fetch_ai_summary(article.content)
        await self.db.create_summary(summary, article.id)

