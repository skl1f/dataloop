from typing import Optional
from pydantic.dataclasses import dataclass


@dataclass
class Message:
    key: str
    value: str


@dataclass
class MongoRequest:
    id: Optional[str] = ""
