from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.now) 