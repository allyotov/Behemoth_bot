from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Subscriber(BaseModel):
    id: int
    last_update: datetime


class NewsItem(BaseModel):
    id: str
    updated_time: datetime
    meeting_time: Optional[datetime]
    text: str