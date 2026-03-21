from fastapi import APIRouter, Query, Request

from src.service.reference import reference_service
from src.service.reference.reference_schema import ReferenceListResponse, ReferenceResponse

router = APIRouter(prefix="/api/reference", tags=["Reference"])


@router.get("", response_model=ReferenceListResponse)
async def list_references(
	request: Request,
	page: int = Query(default=1, ge=1, description="페이지 번호"),
	limit: int = Query(default=20, ge=1, le=100, description="페이지 크기"),
):
	"""레퍼런스 이미지 목록 조회"""
	ctx = request.app.state.ctx
	return reference_service.list_references(ctx, page=page, limit=limit)


@router.get("/{reference_id}", response_model=ReferenceResponse)
async def get_reference(request: Request, reference_id: str):
	"""레퍼런스 이미지 상세 정보 조회"""
	ctx = request.app.state.ctx
	return reference_service.get_reference(ctx, reference_id)

