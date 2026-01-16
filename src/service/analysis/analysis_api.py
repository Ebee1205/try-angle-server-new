"""
Analysis API Router
TryAngle 이미지 분석 및 피드백 API
"""

from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
import os
import time

from service.analysis import analysis_service

# 라우터 등록
router = APIRouter(prefix="/api", tags=["Analysis"])


@router.get("/")
async def root(request: Request):
    """서버 상태 확인"""
    ctx = request.app.state.ctx
    return analysis_service.get_server_status(ctx)


@router.post("/analyze/realtime")
async def analyze_realtime(
    request: Request,
    reference: UploadFile = File(...),
    current_frame: UploadFile = File(...),
    pose_model: str = "movenet"
):
    """
    실시간 프레임 분석

    iOS에서 레퍼런스 이미지와 현재 프레임을 전송하면
    AI 분석 후 피드백을 반환

    Args:
        reference: 레퍼런스 이미지
        current_frame: 현재 프레임
        pose_model: 포즈 모델 선택 ("yolo11" 또는 "movenet")
    """
    ctx = request.app.state.ctx
    
    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as ref_temp:
        ref_temp.write(await reference.read())
        ref_path = ref_temp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as frame_temp:
        frame_temp.write(await current_frame.read())
        frame_path = frame_temp.name

    try:
        return await analysis_service.analyze_realtime(
            ctx=ctx,
            ref_path=ref_path,
            frame_path=frame_path,
            pose_model=pose_model
        )
    finally:
        try:
            os.unlink(ref_path)
            os.unlink(frame_path)
        except:
            pass


@router.post("/feedback/enhanced")
async def get_enhanced_feedback(
    request: Request,
    reference: UploadFile = File(...),
    current_frame: UploadFile = File(...),
    user_level: str = Form("beginner"),
    top_k: int = Form(3),
    session_id: Optional[str] = Form(None)
):
    """
    Phase 1-3 통합 피드백

    - Phase 1.1: Top-K 피드백 (상위 3개만)
    - Phase 1.2: 초보자 친화적 메시지
    - Phase 2.1: 워크플로우 가이드
    - Phase 2.2: 진행도 추적
    - Phase 2.3: 우선순위 분류
    """
    ctx = request.app.state.ctx
    
    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as ref_temp:
        ref_temp.write(await reference.read())
        ref_path = ref_temp.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as frame_temp:
        frame_temp.write(await current_frame.read())
        frame_path = frame_temp.name

    try:
        return await analysis_service.get_enhanced_feedback(
            ctx=ctx,
            ref_path=ref_path,
            frame_path=frame_path,
            user_level=user_level,
            top_k=top_k,
            session_id=session_id
        )
    finally:
        try:
            os.unlink(ref_path)
            os.unlink(frame_path)
        except:
            pass


@router.post("/progress/reset")
async def reset_progress(
    request: Request,
    session_id: str = Form(...)
):
    """진행도 초기화"""
    ctx = request.app.state.ctx
    return await analysis_service.reset_progress(ctx, session_id)


@router.get("/recommendations")
async def get_recommendations(
    request: Request,
    user_image: UploadFile = File(...),
    top_k: int = 3
):
    """
    Phase 3.1: AI 레퍼런스 추천

    사용자 이미지와 유사한 고품질 레퍼런스 추천
    """
    ctx = request.app.state.ctx
    
    # 임시 파일 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(await user_image.read())
        user_path = temp.name

    try:
        return await analysis_service.get_recommendations(
            ctx=ctx,
            user_path=user_path,
            top_k=top_k
        )
    finally:
        try:
            os.unlink(user_path)
        except:
            pass
