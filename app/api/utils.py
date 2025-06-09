"""
Утилита для HTML-парсинга на основе BeautifulSoup.

- `Parser`: извлекает заголовок, контент и внутренние ссылки из статьи Wikipedia-подобного формата.
- Удаляет теги сноски `<sup>`.
- Для родительской статьи собирает ссылки на дочерние.
"""


from dataclasses import dataclass, field

from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin


@dataclass
class Parser:
    parent: bool

    url: str
    html: str

    title: str = field(default=None, init=False)
    content: str = field(default=None, init=False)
    urls: list[str] | None = field(default=None, init=False)
    urls_limit: int = 5

    base_url: str = field(default="https://en.wikipedia.org", init=False)
    wiki_article_pattern: re.Pattern = field(default=re.compile(r'^/wiki/[^:#]+$'), init=False)
    soup: BeautifulSoup = field(init=False)

    def __post_init__(self):
        self.soup = BeautifulSoup(self.html, 'lxml')
        if self.parent:
            self.urls = []

    def parse(self):
        self.title = self.parse_title()
        self.content = self.parse_content()

    def parse_title(self):
        title_tag = self.soup.find('header', class_='mw-body-header').find('h1', class_='firstHeading')
        return title_tag.get_text() if title_tag else "Title"

    def parse_content(self):
        content_body = self.soup.find('div', class_='mw-body-content')

        content_parts = []
        for content_part in content_body.find_all(name=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if content_part.get_text() == 'See also':
                break
            self._del_sup_tag(content_part)
            if self.parent and len(self.urls) < self.urls_limit:
                self.parse_urls(content_part)

            content_parts.append(content_part.get_text())
        return "\n".join(content_parts)
        
    def parse_urls(self, content_part):
        for url in content_part.find_all('a', limit=self.urls_limit - len(self.urls)):
            href = url.get('href')
            if href and self.wiki_article_pattern.match(href):
                full_url = urljoin(self.base_url, href)
                self.urls.append(full_url)

    def _del_sup_tag(self, content_part):
        for sup_tag in content_part.find_all('sup'):
            sup_tag.decompose()


    def generate_data_dict(self) -> dict:
        data = {
            'url': self.url,
            'title': self.title,
            'content': self.content
        }
        return data