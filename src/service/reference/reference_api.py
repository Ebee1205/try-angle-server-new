from fastapi import APIRouter, Depends, Request

from src.service.auth.jwt_auth import require_user
from src.service.reference import reference_service
from src.service.reference.reference_schema import (
	RefCreateRequest,
	RefDeleteRequest,
	RefGetRequest,
	RefListRequest,
	RefListResponse,
	RefResponse,
	RefUpdateRequest,
)

router = APIRouter(prefix="/api/ref", tags=["Reference"])


@router.post("/list", response_model=RefListResponse)
async def list_references(request: Request, payload: RefListRequest, _=Depends(require_user)):
	"""레퍼런스 이미지 목록 조회"""
	ctx = request.app.state.ctx
	return reference_service.list_references(
		ctx,
		page=payload.page,
		limit=payload.limit,
		ctg_id=payload.ctgId,
	)


@router.post("/get", response_model=RefResponse)
async def get_reference(request: Request, payload: RefGetRequest, _=Depends(require_user)):
	"""레퍼런스 이미지 상세 정보 조회"""
	ctx = request.app.state.ctx
	return reference_service.get_reference(ctx, payload.id)


@router.post("/create", response_model=RefResponse)
async def create_reference(request: Request, payload: RefCreateRequest, _=Depends(require_user)):
	"""레퍼런스 이미지 등록"""
	ctx = request.app.state.ctx
	return reference_service.create_reference(ctx, payload)


@router.post("/update", response_model=RefResponse)
async def update_reference(request: Request, payload: RefUpdateRequest, _=Depends(require_user)):
	"""레퍼런스 이미지 수정"""
	ctx = request.app.state.ctx
	return reference_service.update_reference(ctx, payload)


@router.post("/delete")
async def delete_reference(request: Request, payload: RefDeleteRequest, _=Depends(require_user)):
	"""레퍼런스 이미지 삭제"""
	ctx = request.app.state.ctx
	return reference_service.delete_reference(ctx, payload.id)

