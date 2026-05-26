from typing import Any, Optional

from pydantic import BaseModel, Field


class RefListRequest(BaseModel):
    page: int = Field(1, ge=1, description="페이지 번호")
    limit: int = Field(20, ge=1, le=100, description="페이지 크기")
    ctgId: Optional[int] = Field(None, description="카테고리 ID 필터")


class RefGetRequest(BaseModel):
    id: int = Field(..., description="레퍼런스 이미지 ID")


class RefCreateRequest(BaseModel):
    ctgId: int = Field(..., description="카테고리 ID")
    imgUrl: str = Field(..., description="레퍼런스 이미지 경로")
    title: Optional[str] = Field(None, description="이미지 제목")
    desc: Optional[str] = Field(None, description="이미지 설명")
    kwd: Optional[list[Any]] = Field(None, description="키워드 코드 리스트(JSON)")
    aiDoc: Optional[dict[str, Any]] = Field(None, description="AI 가이드라인 JSON")
    expWeight: float = Field(0, description="노출 가중치")
    pri: int = Field(0, description="우선순위")


class RefUpdateRequest(BaseModel):
    id: int = Field(..., description="레퍼런스 이미지 ID")
    ctgId: Optional[int] = Field(None, description="카테고리 ID")
    imgUrl: Optional[str] = Field(None, description="레퍼런스 이미지 경로")
    title: Optional[str] = Field(None, description="이미지 제목")
    desc: Optional[str] = Field(None, description="이미지 설명")
    useCnt: Optional[int] = Field(None, ge=0, description="참조 촬영 횟수")
    kwd: Optional[list[Any]] = Field(None, description="키워드 코드 리스트(JSON)")
    aiDoc: Optional[dict[str, Any]] = Field(None, description="AI 가이드라인 JSON")
    expWeight: Optional[float] = Field(None, description="노출 가중치")
    pri: Optional[int] = Field(None, description="우선순위")


class RefDeleteRequest(BaseModel):
    id: int = Field(..., description="레퍼런스 이미지 ID")


class RefUser(BaseModel):
    userId: int = Field(...)
    nickname: Optional[str] = Field(None)
    fileUrl: Optional[str] = Field(None)

    class Config:
        from_attributes = True


class RefCategory(BaseModel):
    ctgId: int = Field(...)
    ctgName: str = Field(...)

    class Config:
        from_attributes = True


class RefItem(BaseModel):
    imgId: int = Field(...)
    user: RefUser
    imgUrl: str = Field(...)
    ctg: RefCategory
    title: Optional[str] = Field(None)
    desc: Optional[str] = Field(None)
    useCnt: int = Field(...)
    kwd: list[Any] = Field(default_factory=list)
    aiDoc: Optional[dict[str, Any]] = Field(None)
    expWeight: float = Field(...)
    pri: int = Field(...)
    cDate: int = Field(...)
    uDate: int = Field(...)

    class Config:
        from_attributes = True


class RefListResponse(BaseModel):
    items: list[RefItem]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True
