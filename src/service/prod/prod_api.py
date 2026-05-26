from fastapi import APIRouter, Depends, Request

from src.core.responses import build_success_response

from src.service.auth.jwt_auth import require_admin, require_user
from src.service.prod import prod_service
from src.service.prod.prod_schema import (
	ProdCreateRequest,
	ProdDeleteRequest,
	ProdGetRequest,
	ProdListRequest,
	ProdUpdateRequest,
)

router = APIRouter(prefix="/api/prod", tags=["Product"])


@router.post("/list")
async def list_prods(request: Request, payload: ProdListRequest, _=Depends(require_user)):
	"""상품 목록 조회"""
	ctx = request.app.state.ctx
	result = prod_service.list_prods(
		ctx,
		page=payload.page,
		limit=payload.limit,
		p_stat=payload.pStat,
	)
	return build_success_response(result)


@router.post("/get")
async def get_prod(request: Request, payload: ProdGetRequest, _=Depends(require_user)):
	"""상품 조회"""
	ctx = request.app.state.ctx
	result = prod_service.get_prod(ctx, payload.id)
	return build_success_response(result)


@router.post("/create")
async def create_prod(request: Request, payload: ProdCreateRequest, user=Depends(require_admin)):
	"""상품 등록 (Admin)"""
	ctx = request.app.state.ctx
	result = prod_service.create_prod(ctx, payload, user_id=user["id"])
	return build_success_response(result)


@router.post("/update")
async def update_prod(request: Request, payload: ProdUpdateRequest, _=Depends(require_admin)):
	"""상품 수정 (Admin)"""
	ctx = request.app.state.ctx
	result = prod_service.update_prod(ctx, payload)
	return build_success_response(result)


@router.post("/delete")
async def delete_prod(request: Request, payload: ProdDeleteRequest, _=Depends(require_admin)):
	"""상품 삭제 (Admin)"""
	ctx = request.app.state.ctx
	result = prod_service.delete_prod(ctx, payload.id)
	return build_success_response(result)
