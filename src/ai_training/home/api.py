import logging
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from ai_training.home import audit, tools
from ai_training.home.agent import get_agent
from ai_training.settings import get_settings

logger = logging.getLogger(__name__)


def require_key(x_api_key: str = Header(default="")):
    expected = get_settings().home_api_key
    if not expected or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


router = APIRouter(prefix="/home", dependencies=[Depends(require_key)])


class CommandRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)

    @field_validator("session_id", "text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be blank.")
        return cleaned


class CommandResponse(BaseModel):
    reply: str
    needs_confirmation: bool


@router.post("/command", response_model=CommandResponse)
def command(req: CommandRequest):
    try:
        return get_agent(req.session_id).handle(req.text)
    except Exception:
        logger.exception("Home command failed for session %s", req.session_id)
        raise HTTPException(status_code=502, detail="Home agent request failed.")


@router.get("/state")
def state():
    return tools.home.get_state()


@router.get("/audit")
def audit_log(limit: int = Query(50, ge=1, le=500)):
    return audit.get_log(limit)