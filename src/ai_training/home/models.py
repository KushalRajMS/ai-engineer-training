from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)