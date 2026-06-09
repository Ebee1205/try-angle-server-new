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

    # [신규 추가] 실시간 스냅샷 비즈니스 지표 검색용 필터
    category: Optional[str] = Field(None, description="촬영 단계/모드 필터 (예: person, framing_shot)")
    feedback: Optional[str] = Field(None, description="실시간 가이드 안내 메시지 키워드 (Partial Match)")
    reason: Optional[str] = Field(None, description="실패 원인 디테일 키워드 (Partial Match)")
    stuckSec: Optional[int] = Field(None, ge=0, description="최소 정체 시간(초) 조건")
    canCapture: Optional[str] = Field(None, description="촬영 가능 여부 필터 ('true' 또는 'false')")

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

    category: Optional[str] = Field(None, description="촬영 단계/모드 필터")
    feedback: Optional[str] = Field(None, description="실시간 가이드 피드백 문구 검색")
    stuckSec: Optional[int] = Field(None, description="정체 시간 조건 필터")
    canCapture: Optional[str] = Field(None, description="촬영 가능 여부 필터")


class SessionDetailRequest(BaseModel):
    id: str = Field(..., description="세션 ID")
    fromSecSeq: Optional[int] = Field(None, ge=1, description="secSeq 시작 필터")
    toSecSeq: Optional[int] = Field(None, ge=1, description="secSeq 종료 필터")


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
    # [신규 추가] 모니터링용 집계 필드
    maxStuckSec: Optional[float] = Field(None, description="최대 정체 시간(초)")
    snapshotCount: Optional[int] = Field(None, description="해당 세션의 총 스냅샷 수")
    mainFeedback: Optional[str] = Field(None, description="마지막 Vision AI 피드백 메시지")

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    items: list[SessionItem]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True


class SessionRecord(BaseModel):
    tid: int
    fseq: int
    gate: int
    offsetMs: int
    cur: Optional[dict[str, Any]] = None
    res: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    session: SessionItem
    # Flattened list of per-frame records (previously nested under snapshots.records)
    snapshots: list[SessionRecord]
    secCount: int
    recordCount: int

    class Config:
        from_attributes = True