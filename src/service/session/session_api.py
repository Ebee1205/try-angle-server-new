from fastapi import APIRouter, Depends, Request

from src.core.responses import ResponseStatus, build_response_body, build_success_response
from src.service.auth.jwt_auth import require_user
from src.service.session import session_service
from src.service.session.session_schema import (
    SessionDetailRequest,
    SessionEndRequest,
    SessionListRequest,
    SessionListResponse,
    SessionStartRequest,
)


router = APIRouter(prefix="/api/session", tags=["Session"])


def _norm_filter(payload: SessionListRequest) -> tuple[int | None, int | None, int | None, int | None, int | None]:
    z = payload.filter
    if z is not None and not any(v is not None for v in z.model_dump().values()):
        z = None
    return (
        z.userId if z is not None else payload.userId,
        z.imgId if z is not None else payload.imgId,
        z.sStat if z is not None else payload.sStat,
        z.sDate if z is not None else payload.sDate,
        z.eDate if z is not None else payload.eDate,
    )


def _invoke(ctx, op: str, payload, user: dict):
    if op == "L":
        user_id, img_id, s_stat, s_date, e_date = _norm_filter(payload)
        return session_service.list_sessions(
            ctx,
            page=payload.page,
            limit=payload.limit,
            user_id=user_id,
            img_id=img_id,
            s_stat=s_stat,
            sDate=s_date,
            eDate=e_date,
        )
    if op == "D":
        return session_service.get_session_detail(
            ctx,
            session_id=payload.id,
            user_id=user["id"],
            user_role=user.get("role"),
        )
    if op == "S":
        return session_service.start_session(ctx, payload, user_id=user["id"])
    return session_service.end_session(ctx, payload)


@router.post("/list")
async def list_sessions(request: Request, payload: SessionListRequest, _=Depends(require_user)):
    """촬영 세션 목록 조회"""
    ctx = request.app.state.ctx
    result = _invoke(ctx, "L", payload, {})
    return build_success_response(result)


@router.post("/detail")
async def get_session_detail(request: Request, payload: SessionDetailRequest, user=Depends(require_user)):
    """세션 상세 조회"""
    ctx = request.app.state.ctx
    result = _invoke(ctx, "D", payload, user)
    return build_success_response(result)


@router.post("/start")
async def start_session(request: Request, payload: SessionStartRequest, user=Depends(require_user)):
    """촬영 세션 시작"""
    ctx = request.app.state.ctx
    result = _invoke(ctx, "S", payload, user)
    return build_response_body(ResponseStatus.CREATED, result)


@router.post("/end")
async def end_session(request: Request, payload: SessionEndRequest, _=Depends(require_user)):
    """촬영 세션 종료"""
    ctx = request.app.state.ctx
    result = _invoke(ctx, "E", payload, {})

    return build_success_response(result)