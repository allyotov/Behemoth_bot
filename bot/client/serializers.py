from datetime import datetime

from pydantic import BaseModel


class Subscriber(BaseModel):
    id: int
    last_update: datetime