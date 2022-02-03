from re import S
from pydantic import BaseModel


class Meeting(BaseModel):
    name: str
    fragment: str
    comment: str
    time: str
    intramural: int


class NewsItem(BaseModel):
    title: str
    text: str
    time_created: str
    author: str
