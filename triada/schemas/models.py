from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlmodel import Field


class Message(BaseModel):
    id: int = Field(default=None)
    text: str
    peer_id: int
    from_id: int
    attachments: Optional[List[dict]] = Field(default=None)
    date: datetime = Field(default=None)
