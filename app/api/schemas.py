from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Annotated
import re




class UrlSchema(BaseModel):
    url: Annotated[HttpUrl, Field(examples=["https://en.wikipedia.org/wiki/YouTube"])]

    @field_validator("url")
    def validate_wikipedia_url(cls, url: HttpUrl) -> HttpUrl:
        if not re.match(r"^https?://en\.wikipedia\.org/wiki/", str(url)):
            raise ValueError("URL must be from English Wikipedia (e.g., https://en.wikipedia.org/wiki/...)")
        return url
