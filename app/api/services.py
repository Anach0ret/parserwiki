from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
from urllib.parse import urljoin
from dotenv import load_dotenv
import os

from app.api.schemas import UrlSchema
from app.api.crud import DB
from app.api.models import Article

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
            return data["choices"][0]["message"]["content"]


async def fetch(url: str):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, ssl=False) as response:
            if response.status == 200:
                return await response.text()
            else:
                return False


async def parser(html: str, url: str, parent: bool) -> dict:
    data = {
        'url': url,
        'title': None,
        'content': None,
        'links': [],
    }
    base_url = "https://en.wikipedia.org"
    wiki_article_pattern = re.compile(r'^/wiki/[^:#]+$')
    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('header', class_= 'mw-body-header').find('h1', class_= 'firstHeading')
    if title:
        data['title'] = title.get_text()
    else:
        data['title'] = "Title"

    content_body = soup.find('div', class_='mw-body-content')

    content_parts = []
    for content_part in content_body.find_all(name=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if content_part.get_text() == 'See also':
            break
        for sup_tag in content_part.find_all('sup'):
            sup_tag.decompose()

        if len(data['links']) < 5 and parent:
            for link in content_part.find_all('a', limit=5-len(data['links'])):
                href = link.get('href')
                if href and wiki_article_pattern.match(href):
                    full_url = urljoin(base_url, href)
                    data['links'].append(full_url)

        content_parts.append(content_part.get_text())
    data['content'] = "\n".join(content_parts).replace("\n",'')

    return data




class ArticleParserService:
    def __init__(self, url_schema: UrlSchema, db: DB):
        self.url = str(url_schema.url)
        self.db = db

        self.tasks = []


    async def parse(self):
        html_page = await fetch(self.url)

        if not html_page:
            return {"error": "Failed to fetch parent article"}

        parent_article = await parser(html_page, self.url, parent=True)
        db_article = await self.db.create_get_article(data=parent_article)
        self.tasks.append(self.generate_summary(db_article))
        self.tasks.extend([self._parse_create_child(link, db_article) for link in parent_article["links"]])

        result = await self._execute_tasks()

        return {
            "message": f"Parsed article from {self.url}",
            "parent_article": parent_article,
            "result_tasks": result
        }


    async def _execute_tasks(self):
        return await asyncio.gather(*self.tasks, return_exceptions=False)

    async def _parse_create_child(self, link: str, parent: Article):
        print(f'child parse {link}')
        html = await fetch(link)
        if not html:
            return None
        data = await parser(html, link, parent=False)
        return await self.db.create_get_article(data=data, parent=parent)

    async def generate_summary(self, article: Article):
        print('generate summary')
        summary = await fetch_ai_summary(article.content)
        await self.db.create_summary(summary, article.id)

