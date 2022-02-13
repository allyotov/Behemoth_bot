from datetime import datetime
from typing import Optional
from xmlrpc.client import boolean

from pydantic import BaseModel


class Subscriber(BaseModel):
    id: int
    last_update: datetime
    active: boolean
    username: str
    first_name: Optional[str]
    last_name: Optional[str]


class NewsItem(BaseModel):
    id: str
    updated_time: datetime
    meeting_time: Optional[datetime]
    text: str