from datetime import datetime
from pydantic import BaseModel


class NewsItem(BaseModel):
    id: int
    updated_time: datetime
    meeting_time: datetime or None
    text: str


class Subscriber(BaseModel):
    id: int
    last_update: datetime