from typing import Any, Optional

from pydantic import BaseModel, Field


class ReferenceListItem(BaseModel):
	"""레퍼런스 이미지 목록 아이템 스키마"""
	url: str = Field(..., description="이미지 URL")
	title: str = Field(..., description="이미지 제목")
	desc: Optional[str] = Field(None, description="이미지 설명")
	category: Optional[str] = Field(None, description="카테고리")
	u_date: int = Field(..., description="수정 날짜 Unix timestamp")
	c_date: int = Field(..., description="생성 날짜 Unix timestamp")

	class Config:
		from_attributes = True


class ReferenceResponse(BaseModel):
	"""레퍼런스 이미지 상세 응답 스키마"""
	url: str = Field(..., description="이미지 URL")
	title: str = Field(..., description="이미지 제목")
	desc: Optional[str] = Field(None, description="이미지 설명")
	category: Optional[str] = Field(None, description="카테고리")
	u_date: int = Field(..., description="수정 날짜 Unix timestamp")
	c_date: int = Field(..., description="생성 날짜 Unix timestamp")
	ai_data: Any = Field(..., description="가공하지 않은 원본 AI 분석 JSON")

	class Config:
		from_attributes = True


class ReferenceListResponse(BaseModel):
	"""레퍼런스 이미지 목록 응답 스키마"""
	items: list[ReferenceListItem]
	total: int = Field(..., description="전체 개수")
	page: int = Field(..., description="현재 페이지")
	limit: int = Field(..., description="페이지 크기")

	class Config:
		from_attributes = True

