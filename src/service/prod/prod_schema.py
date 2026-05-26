from typing import Optional

from pydantic import BaseModel, Field


class ProdListRequest(BaseModel):
	"""상품 목록 조회 요청 스키마"""
	page: int = Field(1, ge=1, description="페이지 번호")
	limit: int = Field(20, ge=1, le=100, description="페이지 크기")
	pStat: Optional[int] = Field(None, description="상품 상태 필터 (0: INACTIVE, 1: ACTIVE, 2: SOLD_OUT)")


class ProdCreateRequest(BaseModel):
	"""상품 등록 요청 스키마"""
	name: str = Field(..., description="상품명")
	brand: Optional[str] = Field(None, description="상품 브랜드")
	price: int = Field(0, ge=0, description="상품 가격")
	thumbUrl: Optional[str] = Field(None, description="상품 썸네일 경로")
	pStat: int = Field(1, description="상품 상태 (0: INACTIVE, 1: ACTIVE, 2: SOLD_OUT)")


class ProdGetRequest(BaseModel):
	"""상품 조회 요청 스키마"""
	id: int = Field(..., description="상품 ID")


class ProdUpdateRequest(BaseModel):
	"""상품 수정 요청 스키마"""
	id: int = Field(..., description="상품 ID")
	name: Optional[str] = Field(None, description="상품명")
	brand: Optional[str] = Field(None, description="상품 브랜드")
	price: Optional[int] = Field(None, ge=0, description="상품 가격")
	thumbUrl: Optional[str] = Field(None, description="상품 썸네일 경로")
	pStat: Optional[int] = Field(None, description="상품 상태 (0: INACTIVE, 1: ACTIVE, 2: SOLD_OUT)")


class ProdDeleteRequest(BaseModel):
	"""상품 삭제 요청 스키마"""
	id: int = Field(..., description="상품 ID")


class ProdItem(BaseModel):
	"""상품 아이템 스키마"""
	id: int = Field(..., description="상품 ID")
	userId: int = Field(..., description="상품 등록 사용자 ID")
	name: str = Field(..., description="상품명")
	brand: Optional[str] = Field(None, description="상품 브랜드")
	price: int = Field(..., description="상품 가격")
	thumbUrl: Optional[str] = Field(None, description="상품 썸네일 경로")
	pStat: int = Field(..., description="상품 상태")
	cDate: int = Field(..., description="생성일 Unix Timestamp")
	uDate: int = Field(..., description="수정일 Unix Timestamp")

	class Config:
		from_attributes = True


class ProdListResponse(BaseModel):
	"""상품 목록 응답 스키마"""
	items: list[ProdItem]
	total: int = Field(..., description="전체 개수")
	page: int = Field(..., description="현재 페이지")
	limit: int = Field(..., description="페이지 크기")

	class Config:
		from_attributes = True
