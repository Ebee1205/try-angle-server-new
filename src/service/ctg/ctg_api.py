from fastapi import APIRouter, Depends, Request

from src.service.auth.jwt_auth import require_user
from src.service.ctg import ctg_service
from src.service.ctg.ctg_schema import (
    CtgCreateRequest,
    CtgDeleteRequest,
    CtgGetRequest,
    CtgListRequest,
    CtgListResponse,
    CtgItem,
    CtgUpdateRequest,
)

router = APIRouter(prefix="/api/ctg", tags=["Category"])


@router.post("/list", response_model=CtgListResponse)
async def list_ctgs(request: Request, payload: CtgListRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    return ctg_service.list_ctgs(ctx, page=payload.page, limit=payload.limit)


@router.post("/get", response_model=CtgItem)
async def get_ctg(request: Request, payload: CtgGetRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    return ctg_service.get_ctg(ctx, payload.id)


@router.post("/create", response_model=CtgItem)
async def create_ctg(request: Request, payload: CtgCreateRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    return ctg_service.create_ctg(ctx, payload)


@router.post("/update", response_model=CtgItem)
async def update_ctg(request: Request, payload: CtgUpdateRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    return ctg_service.update_ctg(ctx, payload)


@router.post("/delete")
async def delete_ctg(request: Request, payload: CtgDeleteRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    return ctg_service.delete_ctg(ctx, payload.id)
