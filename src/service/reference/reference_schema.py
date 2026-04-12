from typing import Any, Optional

from pydantic import BaseModel, Field


class RefListRequest(BaseModel):
	"""레퍼런스 이미지 목록 조회 요청 스키마"""
	page: int = Field(1, ge=1, description="페이지 번호")
	limit: int = Field(20, ge=1, le=100, description="페이지 크기")
	ctgId: Optional[str] = Field(None, description="카테고리 ID")


class RefGetRequest(BaseModel):
	"""레퍼런스 이미지 상세 조회 요청 스키마"""
	id: str = Field(..., description="이미지 ID")


class RefCreateRequest(BaseModel):
	"""레퍼런스 이미지 등록 요청 스키마"""
	userId: str = Field(..., description="등록 사용자 ID")
	ctgId: str = Field(..., description="카테고리 ID")
	imgUrl: str = Field(..., description="이미지 URL")
	title: Optional[str] = Field(None, description="이미지 제목")
	desc: Optional[str] = Field(None, description="이미지 설명")
	kwd: Optional[list[str]] = Field(default_factory=list, description="키워드 코드 리스트")
	aiDocId: Optional[str] = Field(None, description="MongoDB 분석 문서 ID")
	expWeight: float = Field(0, description="노출 가중치")
	pri: int = Field(0, description="우선순위")


class RefUpdateRequest(BaseModel):
	"""레퍼런스 이미지 수정 요청 스키마"""
	id: str = Field(..., description="이미지 ID")
	ctgId: Optional[str] = Field(None, description="카테고리 ID")
	imgUrl: Optional[str] = Field(None, description="이미지 URL")
	title: Optional[str] = Field(None, description="이미지 제목")
	desc: Optional[str] = Field(None, description="이미지 설명")
	kwd: Optional[list[str]] = Field(None, description="키워드 코드 리스트")
	aiDocId: Optional[str] = Field(None, description="MongoDB 분석 문서 ID")
	expWeight: Optional[float] = Field(None, description="노출 가중치")
	pri: Optional[int] = Field(None, description="우선순위")


class RefDeleteRequest(BaseModel):
	"""레퍼런스 이미지 삭제 요청 스키마"""
	id: str = Field(..., description="이미지 ID")


class RefListItem(BaseModel):
	"""레퍼런스 이미지 목록 아이템 스키마"""
	id: str = Field(..., description="이미지 ID")
	userId: str = Field(..., description="등록 사용자 ID")
	ctgId: str = Field(..., description="카테고리 ID")
	imgUrl: str = Field(..., description="이미지 URL")
	title: str = Field(..., description="이미지 제목")
	desc: Optional[str] = Field(None, description="이미지 설명")
	categoryName: Optional[str] = Field(None, description="카테고리 이름")
	useCnt: int = Field(0, description="사용 횟수")
	kwd: Optional[list[str]] = Field(default_factory=list, description="키워드 코드 리스트")
	aiDocId: Optional[str] = Field(None, description="MongoDB 분석 문서 ID")
	expWeight: float = Field(0, description="노출 가중치")
	pri: int = Field(0, description="우선순위")
	cDate: int = Field(..., description="생성 날짜 Unix timestamp")
	uDate: int = Field(..., description="수정 날짜 Unix timestamp")

	class Config:
		from_attributes = True


class RefResponse(BaseModel):
	"""레퍼런스 이미지 상세 응답 스키마"""
	id: str = Field(..., description="이미지 ID")
	userId: str = Field(..., description="등록 사용자 ID")
	ctgId: str = Field(..., description="카테고리 ID")
	imgUrl: str = Field(..., description="이미지 URL")
	title: str = Field(..., description="이미지 제목")
	desc: Optional[str] = Field(None, description="이미지 설명")
	categoryName: Optional[str] = Field(None, description="카테고리 이름")
	useCnt: int = Field(0, description="사용 횟수")
	kwd: Optional[list[str]] = Field(default_factory=list, description="키워드 코드 리스트")
	aiDocId: Optional[str] = Field(None, description="MongoDB 분석 문서 ID")
	expWeight: float = Field(0, description="노출 가중치")
	pri: int = Field(0, description="우선순위")
	cDate: int = Field(..., description="생성 날짜 Unix timestamp")
	uDate: int = Field(..., description="수정 날짜 Unix timestamp")
	ai_data: Any = Field(..., description="가공하지 않은 원본 AI 분석 JSON")

	class Config:
		from_attributes = True


class RefListResponse(BaseModel):
	"""레퍼런스 이미지 목록 응답 스키마"""
	items: list[RefListItem]
	total: int = Field(..., description="전체 개수")
	page: int = Field(..., description="현재 페이지")
	limit: int = Field(..., description="페이지 크기")

	class Config:
		from_attributes = True

