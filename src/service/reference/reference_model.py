"""
Reference Model
참고용 이미지 관리 모델
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ReferenceModel(BaseModel):
    """Reference DB 스키마"""
    id: Optional[int] = None
    image_url: str
    source: str  # pinterest, instagram, internal
    external_id: Optional[str] = None  # 외부 플랫폼 ID (중복 수집 방지)
    category: str  # 태그/카테고리 (전신, 셀카, 카페 등)
    popularity_score: int = 0  # 외부 선호도 + 내부 가중치
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferenceCreateRequest(BaseModel):
    """Reference 생성 요청"""
    image_url: str
    source: str
    category: str
    external_id: Optional[str] = None
    popularity_score: int = 0


class ReferenceResponse(BaseModel):
    """Reference 응답"""
    id: int
    image_url: str
    source: str
    category: str
    popularity_score: int
    is_active: bool
    created_at: datetime


class PinterestSearchRequest(BaseModel):
    """Pinterest 검색 요청"""
    category: str  # 검색할 카테고리 태그
    limit: int = 10  # 반환할 이미지 개수


class PinterestSearchResponse(BaseModel):
    """Pinterest 검색 응답"""
    images: list[dict]  # [{"url": "...", "external_id": "...", "title": "..."}, ...]
    total_count: int
    source: str = "pinterest"
