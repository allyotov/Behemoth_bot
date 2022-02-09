from datetime import datetime

from dataclasses import dataclass


@dataclass
class Subscriber:
    id: int
    last_update: datetime