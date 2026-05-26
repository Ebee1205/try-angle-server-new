from fastapi import APIRouter, Depends, Request

from src.core.responses import ResponseStatus, build_response_body, build_success_response
from src.service.auth.jwt_auth import require_user
from src.service.session import session_service
from src.service.session.session_schema import SessionEndRequest, SessionStartRequest


router = APIRouter(prefix="/api/session", tags=["Session"])


@router.post("/start")
async def start_session(request: Request, payload: SessionStartRequest, user=Depends(require_user)):
    """촬영 세션 시작"""
    ctx = request.app.state.ctx
    result = session_service.start_session(ctx, payload, user_id=user["id"])
    return build_response_body(ResponseStatus.CREATED, result)


@router.post("/end")
async def end_session(request: Request, payload: SessionEndRequest, _=Depends(require_user)):
    """촬영 세션 종료"""
    ctx = request.app.state.ctx
    result = session_service.end_session(ctx, payload)
    return build_success_response(result)