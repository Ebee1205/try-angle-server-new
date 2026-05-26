from enum import IntEnum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SessionStatus(IntEnum):
    READY = 0
    COMPLETED = 1
    FAILED = 2


class SessionStartRequest(BaseModel):
    imgId: int = Field(..., description="레퍼런스 이미지 ID")
    device: Optional[dict[str, Any]] = Field(None, description="디바이스 메타데이터")


class SessionEndRequest(BaseModel):
    id: str = Field(..., description="세션 ID")


class SessionItem(BaseModel):
    id: str
    userId: int
    imgId: int
    sDate: int
    eDate: Optional[int] = None
    device: Optional[dict[str, Any]] = None
    sStat: int
    cDate: int
    uDate: int

    class Config:
        from_attributes = True