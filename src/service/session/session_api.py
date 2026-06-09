from fastapi import APIRouter, Depends, Request

from src.core.responses import ResponseStatus, build_response_body, build_success_response
from src.service.auth.jwt_auth import require_user
from src.service.system import system_service
from src.service.session import session_service
from src.service.session.session_schema import (
    SessionDetailRequest,
    SessionEndRequest,
    SessionListRequest,
    SessionListResponse,
    SessionStartRequest,
)


router = APIRouter(prefix="/api/session", tags=["Session"])


@router.post("/list")
async def list_sessions(request: Request, payload: SessionListRequest, _=Depends(require_user)):
    """촬영 세션 목록 조회 (신규 피드백 검색 조건 포함)"""
    ctx = request.app.state.ctx
    req_filter = payload.filter

    # filter가 빈 객체 {}로 왔을 때 None과 동일하게 처리
    if req_filter is not None and not any(v is not None for v in req_filter.model_dump().values()):
        req_filter = None

    # filter 객체가 있으면 내부 값을 쓰고, 없으면 루트 flat body 값을 바인딩 (기존 로직 유지 확장)
    user_id    = req_filter.userId    if req_filter is not None else payload.userId
    img_id     = req_filter.imgId     if req_filter is not None else payload.imgId
    s_stat     = req_filter.sStat     if req_filter is not None else payload.sStat
    sDate      = req_filter.sDate     if req_filter is not None else payload.sDate
    eDate      = req_filter.eDate     if req_filter is not None else payload.eDate
    category   = req_filter.category  if req_filter is not None else payload.category
    feedback   = req_filter.feedback  if req_filter is not None else payload.feedback
    stuckSec   = req_filter.stuckSec  if req_filter is not None else payload.stuckSec
    canCapture = req_filter.canCapture if req_filter is not None else payload.canCapture

    result = session_service.list_sessions(
        ctx,
        page=payload.page,
        limit=payload.limit,
        user_id=user_id,
        img_id=img_id,
        s_stat=s_stat,
        sDate=sDate,
        eDate=eDate,
        category=category,
        feedback=feedback,
        stuckSec=stuckSec,
        canCapture=canCapture,
    )
    return build_success_response(result)


@router.post("/detail")
async def get_session_detail(request: Request, payload: SessionDetailRequest, user=Depends(require_user)):
    """세션 상세 및 스냅샷 로그 조회"""
    ctx = request.app.state.ctx
    result = session_service.get_session_detail(
        ctx,
        session_id=payload.id,
        user_id=user["id"],
        user_role=user.get("role"),
        from_sec_seq=payload.fromSecSeq,
        to_sec_seq=payload.toSecSeq,
    )
    return build_success_response(result)


@router.post("/start")
async def start_session(request: Request, payload: SessionStartRequest, user=Depends(require_user)):
    """촬영 세션 시작"""
    ctx = request.app.state.ctx
    result = session_service.start_session(ctx, payload, user_id=user["id"])
    return build_response_body(ResponseStatus.CREATED, result)


@router.post("/end")
async def end_session(request: Request, payload: SessionEndRequest, user=Depends(require_user)):
    """촬영 세션 종료"""
    ctx = request.app.state.ctx
    result = session_service.end_session(ctx, payload)

    # 세션 종료 시 Redis 버퍼를 SQL로 일괄 적재
    try:
        flush_result = await system_service.flush_snapshot_session_to_db(
            ctx,
            s_id=payload.id,
            user_id=user["id"],
            delete_after=True,
        )
        result = {**result.model_dump(), "snapshotFlush": flush_result}
    except Exception as e:
        if ctx.log:
            ctx.log.warning(f"Session ended but snapshot flush failed: {e}")
        pass

    return build_success_response(result)