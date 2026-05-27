from fastapi import APIRouter, Depends, Request

from src.core.responses import build_success_response
from src.service.auth.jwt_auth import require_admin, require_user
from src.service.snap import snap_service
from src.service.snap.snap_schema import (
    SnapCreateRequest,
    SnapDeleteRequest,
    SnapGetRequest,
    SnapListRequest,
    SnapUpdateRequest,
)

router = APIRouter(prefix="/api/snap", tags=["Snap"])


@router.post("/list")
async def list_snaps(request: Request, payload: SnapListRequest, _=Depends(require_user)):
    """스냅 목록 조회"""
    ctx = request.app.state.ctx
    req_filter = payload.filter

    user_id = req_filter.userId if req_filter is not None else payload.userId
    prod_id = req_filter.prodId if req_filter is not None else payload.prodId
    img_id = req_filter.imgId if req_filter is not None else payload.imgId
    from_date = req_filter.fromDate if req_filter is not None else payload.fromDate
    to_date = req_filter.toDate if req_filter is not None else payload.toDate

    result = snap_service.list_snaps(
        ctx,
        page=payload.page,
        limit=payload.limit,
        user_id=user_id,
        prod_id=prod_id,
        img_id=img_id,
        from_date=from_date,
        to_date=to_date,
        sort_by=payload.sortBy,
        sort_order=payload.sortOrder,
    )
    return build_success_response(result)


@router.post("/get")
async def get_snap(request: Request, payload: SnapGetRequest, _=Depends(require_user)):
    """스냅 조회"""
    ctx = request.app.state.ctx
    result = snap_service.get_snap(ctx, payload.id)
    return build_success_response(result)


@router.post("/create")
async def create_snap(request: Request, payload: SnapCreateRequest, user=Depends(require_user)):
    """스냅 등록"""
    ctx = request.app.state.ctx
    result = snap_service.create_snap(ctx, payload, user_id=user["id"])
    return build_success_response(result)


@router.post("/update")
async def update_snap(request: Request, payload: SnapUpdateRequest, _=Depends(require_admin)):
    """스냅 수정 (Admin)"""
    ctx = request.app.state.ctx
    result = snap_service.update_snap(ctx, payload)
    return build_success_response(result)


@router.post("/delete")
async def delete_snap(request: Request, payload: SnapDeleteRequest, _=Depends(require_admin)):
    """스냅 삭제 (Admin)"""
    ctx = request.app.state.ctx
    result = snap_service.delete_snap(ctx, payload.id)
    return build_success_response(result)
