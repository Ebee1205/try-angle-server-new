"""
Reference API Router
참고용 이미지 관리 API
"""

from fastapi import APIRouter, Request, Query
from typing import Optional

from service.reference.reference_service import get_reference_service
from service.reference.reference_model import ReferenceCreateRequest

# 라우터 등록
router = APIRouter(prefix="/api/reference", tags=["Reference"])


@router.get("/pinterest/search")
async def search_pinterest(
    request: Request,
    category: str = Query(..., description="검색 카테고리 (전신, 셀카, 카페 등)"),
    limit: int = Query(10, ge=1, le=50, description="반환할 이미지 개수"),
    auto_save: bool = Query(False, description="결과 자동 저장 여부")
):
    """
    Pinterest에서 카테고리로 이미지 검색
    
    - 카테고리 태그를 요청으로 전송
    - Pinterest에서 해당 태그 검색
    - 이미지 URL 리스트 반환
    - (선택) 검색 결과 자동 저장
    
    예시:
    ```
    GET /api/reference/pinterest/search?category=전신&limit=10
    ```
    
    응답:
    ```json
    {
      "images": [
        {
          "url": "https://example.com/image1.jpg",
          "external_id": "pin_123",
          "title": "Full body pose",
          "description": ""
        }
      ],
      "total_count": 10,
      "source": "pinterest"
    }
    ```
    """
    ctx = request.app.state.ctx
    service = get_reference_service(ctx)
    
    return await service.search_pinterest(
        category=category,
        limit=limit,
        auto_save=auto_save
    )


@router.post("/create")
async def create_reference(
    request: Request,
    body: ReferenceCreateRequest
):
    """
    Reference 수동 생성
    
    직접 이미지 URL을 제공하여 Reference 저장
    """
    ctx = request.app.state.ctx
    service = get_reference_service(ctx)
    
    return await service.create_reference(body)


@router.get("/list")
async def get_references(
    request: Request,
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(50, ge=1, le=200, description="한 페이지당 개수"),
    offset: int = Query(0, ge=0, description="시작 위치")
):
    """
    저장된 Reference 목록 조회
    
    예시:
    ```
    GET /api/reference/list?category=전신&limit=20&offset=0
    ```
    """
    ctx = request.app.state.ctx
    service = get_reference_service(ctx)
    
    return await service.get_references(
        category=category,
        is_active=True,
        limit=limit,
        offset=offset
    )


@router.get("/category/{category}")
async def get_references_by_category(
    request: Request,
    category: str,
    limit: int = Query(20, ge=1, le=100, description="반환할 개수")
):
    """
    카테고리별 Reference 조회 (인기도 순)
    
    예시:
    ```
    GET /api/reference/category/전신?limit=10
    ```
    """
    ctx = request.app.state.ctx
    service = get_reference_service(ctx)
    
    return await service.get_reference_by_category(
        category=category,
        limit=limit
    )


@router.patch("/{ref_id}")
async def update_reference(
    request: Request,
    ref_id: int,
    is_active: Optional[bool] = Query(None),
    popularity_score: Optional[int] = Query(None),
    category: Optional[str] = Query(None)
):
    """
    Reference 업데이트
    
    예시:
    ```
    PATCH /api/reference/1?is_active=true&popularity_score=100
    ```
    """
    ctx = request.app.state.ctx
    service = get_reference_service(ctx)
    
    return await service.update_reference(
        ref_id=ref_id,
        is_active=is_active,
        popularity_score=popularity_score,
        category=category
    )


@router.delete("/{ref_id}")
async def delete_reference(
    request: Request,
    ref_id: int
):
    """
    Reference 삭제 (soft delete)
    
    예시:
    ```
    DELETE /api/reference/1
    ```
    """
    ctx = request.app.state.ctx
    service = get_reference_service(ctx)
    
    return await service.delete_reference(ref_id)
