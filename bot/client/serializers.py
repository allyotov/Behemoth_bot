from datetime import datetime
from typing import Optional
from xmlrpc.client import boolean

from pydantic import BaseModel


class Subscriber(BaseModel):
    id: int
    last_update: datetime
    active: boolean


class NewsItem(BaseModel):
    id: str
    updated_time: datetime
    meeting_time: Optional[datetime]
    text: str