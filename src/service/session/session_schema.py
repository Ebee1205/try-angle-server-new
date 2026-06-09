from enum import IntEnum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SessionStatus(IntEnum):
    READY = 0
    COMPLETED = 1
    AUTO_TERM = 2
    FAILED = 3


class SessionStartRequest(BaseModel):
    imgId: int = Field(..., description="레퍼런스 이미지 ID")
    device: Optional[dict[str, Any]] = Field(None, description="디바이스 메타데이터")


class SessionEndRequest(BaseModel):
    id: str = Field(..., description="세션 ID")


class SessionListFilter(BaseModel):
    userId: Optional[int] = Field(None, description="사용자 ID 필터")
    imgId: Optional[int] = Field(None, description="레퍼런스 이미지 ID 필터")
    sStat: Optional[int] = Field(None, description="세션 상태 필터")
    sDate: Optional[int] = Field(None, description="시작일(from) Unix Timestamp")
    eDate: Optional[int] = Field(None, description="시작일(to) Unix Timestamp")

class SessionListRequest(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    limit: int = Field(20, ge=1, le=100, description="페이지 크기")
    filter: Optional[SessionListFilter] = Field(None, description="목록 필터")

    # 하위 호환: 기존 flat body 지원
    userId: Optional[int] = Field(None, description="사용자 ID 필터")
    imgId: Optional[int] = Field(None, description="레퍼런스 이미지 ID 필터")
    sStat: Optional[int] = Field(None, description="세션 상태 필터")
    sDate: Optional[int] = Field(None, description="시작일(from) Unix Timestamp")
    eDate: Optional[int] = Field(None, description="시작일(to) Unix Timestamp")


class SessionDetailRequest(BaseModel):
    id: str = Field(..., description="세션 ID")


class SessionItem(BaseModel):
    id: str
    userId: int
    userName: Optional[str] = None
    imgId: int
    sDate: int
    eDate: Optional[int] = None
    device: Optional[dict[str, Any]] = None
    sStat: int
    cDate: int
    uDate: int

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    items: list[SessionItem]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    session: SessionItem

    class Config:
        from_attributes = True