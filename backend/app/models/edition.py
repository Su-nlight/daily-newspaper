from pydantic import BaseModel

from app.models.article import Article


class Edition(BaseModel):
    id: str
    date: str
    headline: str
    summary: str
    stories: list[Article]
