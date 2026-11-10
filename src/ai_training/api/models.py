from typing import Optional
from pydantic import BaseModel, Field, field_validator

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(default=3, ge=1)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned_question= value.strip()

        if not cleaned_question:
            raise ValueError("Question cannot be blank.")
        return cleaned_question

class SourceItem(BaseModel):
    source: str
    chunk_index: Optional[int] = None

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]

class IngestResponse(BaseModel):
    filename: str
    chunks: int
    message: str