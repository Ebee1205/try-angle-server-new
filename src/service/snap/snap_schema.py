from typing import Optional

from pydantic import BaseModel, Field


class SnapGender:
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class SnapListRequest(BaseModel):
    """스냅 목록 조회 요청 스키마"""
    page: int = Field(1, ge=1, description="페이지 번호")
    limit: int = Field(20, ge=1, le=100, description="페이지 크기")

    # reference_schema 스타일: filter 내부에 검색 조건을 담는다.
    filter: Optional["SnapListFilter"] = Field(None, description="목록 필터")

    # 하위 호환: 기존 flat body를 보내는 클라이언트 지원
    userId: Optional[int] = Field(None, description="사용자 ID 필터")
    prodId: Optional[int] = Field(None, description="상품 ID 필터")
    imgId: Optional[int] = Field(None, description="레퍼런스 이미지 ID 필터")
    fromDate: Optional[int] = Field(None, description="생성일 시작 Unix Timestamp(ms)")
    toDate: Optional[int] = Field(None, description="생성일 종료 Unix Timestamp(ms)")
    sortBy: str = Field("cDate", description="정렬 컬럼 (cDate, uDate, viewCnt, id)")
    sortOrder: str = Field("desc", description="정렬 방향 (asc, desc)")


class SnapListFilter(BaseModel):
    userId: Optional[int] = Field(None, description="사용자 ID 필터")
    prodId: Optional[int] = Field(None, description="상품 ID 필터")
    imgId: Optional[int] = Field(None, description="레퍼런스 이미지 ID 필터")
    fromDate: Optional[int] = Field(None, description="생성일 시작 Unix Timestamp(ms)")
    toDate: Optional[int] = Field(None, description="생성일 종료 Unix Timestamp(ms)")


class SnapGetRequest(BaseModel):
    """스냅 조회 요청 스키마"""
    id: int = Field(..., description="스냅 ID")


class SnapCreateRequest(BaseModel):
    """스냅 등록 요청 스키마"""
    prodId: int = Field(..., description="상품 ID")
    imgId: int = Field(..., description="레퍼런스 이미지 ID")
    sId: str = Field(..., description="세션 ID")
    snapUrl: str = Field(..., description="스냅 이미지 경로")
    comment: Optional[str] = Field(None, description="후기")
    gender: int = Field(SnapGender.UNKNOWN, description="성별 (0: UNKNOWN, 1: MALE, 2: FEMALE)")
    userH: Optional[float] = Field(None, description="키")
    userW: Optional[float] = Field(None, description="몸무게")


class SnapUpdateRequest(BaseModel):
    """스냅 수정 요청 스키마"""
    id: int = Field(..., description="스냅 ID")
    prodId: Optional[int] = Field(None, description="상품 ID")
    imgId: Optional[int] = Field(None, description="레퍼런스 이미지 ID")
    sId: Optional[str] = Field(None, description="세션 ID")
    snapUrl: Optional[str] = Field(None, description="스냅 이미지 경로")
    comment: Optional[str] = Field(None, description="후기")
    gender: Optional[int] = Field(None, description="성별 (0: UNKNOWN, 1: MALE, 2: FEMALE)")
    userH: Optional[float] = Field(None, description="키")
    userW: Optional[float] = Field(None, description="몸무게")
    viewCnt: Optional[int] = Field(None, ge=0, description="조회수")


class SnapDeleteRequest(BaseModel):
    """스냅 삭제 요청 스키마"""
    id: int = Field(..., description="스냅 ID")


class SnapItem(BaseModel):
    """스냅 아이템 스키마"""
    id: int = Field(..., description="스냅 ID")
    userId: int = Field(..., description="유저 ID")
    userName: Optional[str] = Field(None, description="유저명")
    prodId: int = Field(..., description="상품 ID")
    imgId: int = Field(..., description="레퍼런스 이미지 ID")
    sId: Optional[str] = Field(None, description="세션 ID")
    snapUrl: str = Field(..., description="스냅 이미지 경로")
    comment: Optional[str] = Field(None, description="후기")
    gender: int = Field(..., description="성별")
    userH: Optional[float] = Field(None, description="키")
    userW: Optional[float] = Field(None, description="몸무게")
    viewCnt: int = Field(..., description="조회수")
    cDate: int = Field(..., description="생성일 Unix Timestamp")
    uDate: int = Field(..., description="수정일 Unix Timestamp")

    class Config:
        from_attributes = True


class SnapListItem(BaseModel):
    """스냅 목록 아이템 스키마 (요약)"""
    id: int = Field(..., description="스냅 ID")
    userId: int = Field(..., description="유저 ID")
    userName: Optional[str] = Field(None, description="유저명")
    prodId: int = Field(..., description="상품 ID")
    imgId: int = Field(..., description="레퍼런스 이미지 ID")
    sId: Optional[str] = Field(None, description="세션 ID")
    snapUrl: str = Field(..., description="스냅 이미지 경로")
    viewCnt: int = Field(..., description="조회수")
    cDate: int = Field(..., description="생성일 Unix Timestamp")
    uDate: int = Field(..., description="수정일 Unix Timestamp")

    class Config:
        from_attributes = True


class SnapListResponse(BaseModel):
    """스냅 목록 응답 스키마"""
    items: list[SnapListItem]
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    limit: int = Field(..., description="페이지 크기")

    class Config:
        from_attributes = True
