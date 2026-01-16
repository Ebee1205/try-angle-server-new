"""
Analysis Service
TryAngle 이미지 분석 비즈니스 로직
"""

import sys
import os
import time
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List

# TryAngle 코드 import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(project_root, "src", "Multi", "version3"))
sys.path.append(os.path.join(project_root, "src", "Multi", "version3", "utils"))

from analysis.image_comparator import ImageComparator

# Phase 1-3 통합
try:
    from utils.feedback_formatter import FeedbackFormatter
    from utils.workflow_guide import WorkflowGuide
    from utils.progress_tracker import ProgressTracker
    from utils.priority_system import PriorityClassifier
    from utils.reference_recommender import ReferenceRecommender
    PHASE_1_3_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️ Phase 1-3 features not available: {e}")
    PHASE_1_3_AVAILABLE = False

# 글로벌 진행도 트래커 (세션별 관리)
_progress_trackers = {}  # {session_id: ProgressTracker}


def get_server_status(ctx) -> Dict:
    """서버 상태 확인"""
    return {
        "message": "TryAngle iOS Backend (Phase 1-3 Enhanced)",
        "version": "2.0.0",
        "status": "running ✅",
        "features": {
            "phase_1_3": PHASE_1_3_AVAILABLE,
            "top_k_feedback": PHASE_1_3_AVAILABLE,
            "workflow_guide": PHASE_1_3_AVAILABLE,
            "progress_tracking": PHASE_1_3_AVAILABLE,
            "recommendations": PHASE_1_3_AVAILABLE
        }
    }


async def analyze_realtime(
    ctx,
    ref_path: str,
    frame_path: str,
    pose_model: str = "movenet"
) -> JSONResponse:
    """실시간 프레임 분석"""
    start_time = time.time()
    
    # Phase 2-4: MoveNet 옵션 설정
    use_movenet = (pose_model.lower() == "movenet")

    try:
        ctx.log.info(f"📸 분석 시작...")
        ctx.log.info(f"   레퍼런스: {ref_path}")
        ctx.log.info(f"   현재 프레임: {frame_path}")
        ctx.log.info(f"   포즈 모델: {pose_model.upper()}")

        # TryAngle 분석 (기존 Python 코드 활용)
        # Phase 2-4: MoveNet 옵션 전달
        comparator = ImageComparator(ref_path, frame_path, use_movenet=use_movenet)
        comparison = comparator.compare()

        # 사용자 피드백 추출 (행동 가능한 것만)
        user_feedback = extract_user_feedback(comparison)

        # 카메라 설정 추출 (자동 조정용)
        camera_settings = extract_camera_settings(comparison)

        elapsed = time.time() - start_time
        ctx.log.info(f"✅ 분석 완료! ({elapsed:.3f}초)")
        ctx.log.info(f"   피드백 {len(user_feedback)}개 생성")

        return JSONResponse({
            "userFeedback": user_feedback,
            "cameraSettings": camera_settings,
            "processingTime": f"{elapsed:.3f}s",
            "timestamp": time.time()
        })

    except Exception as e:
        ctx.log.error(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "error": str(e),
            "userFeedback": [],
            "cameraSettings": {}
        }, status_code=500)


async def get_enhanced_feedback(
    ctx,
    ref_path: str,
    frame_path: str,
    user_level: str = "beginner",
    top_k: int = 3,
    session_id: Optional[str] = None
) -> JSONResponse:
    """Phase 1-3 통합 피드백"""
    
    if not PHASE_1_3_AVAILABLE:
        return JSONResponse({
            "error": "Phase 1-3 features not available"
        }, status_code=503)

    start_time = time.time()

    try:
        ctx.log.info(f"📸 Enhanced 분석 시작 (user_level={user_level}, top_k={top_k})...")

        # 이미지 비교
        comparator = ImageComparator(ref_path, frame_path)
        raw_feedback = comparator.get_prioritized_feedback()

        # Phase 1.1 & 1.2: 피드백 포맷팅
        formatter = FeedbackFormatter(user_level=user_level)
        formatted = formatter.format_top_k(raw_feedback, top_k=top_k, include_style=True)
        display_text = formatter.format_for_display(formatted)

        # Phase 2.1: 워크플로우 가이드
        workflow_guide = WorkflowGuide()
        workflow_steps = workflow_guide.organize_by_workflow(raw_feedback)
        workflow_text = workflow_guide.format_workflow_text(workflow_steps, show_all=False)

        # Phase 2.3: 우선순위 분류
        priority_groups = PriorityClassifier.group_by_priority(raw_feedback)

        # Phase 2.2: 진행도 추적
        progress_data = None
        if session_id:
            if session_id not in _progress_trackers:
                # 첫 촬영 - 진행도 트래커 생성
                _progress_trackers[session_id] = ProgressTracker()
                _progress_trackers[session_id].set_initial_state(raw_feedback)
                progress = {
                    'overall_score': _progress_trackers[session_id].history[0]['score'],
                    'progress_percent': 0,
                    'attempt_number': 1,
                    'is_first': True
                }
            else:
                # 후속 촬영 - 진행도 업데이트
                progress = _progress_trackers[session_id].update_progress(raw_feedback)
                progress['is_first'] = False

            progress_text = _progress_trackers[session_id].format_progress_text(progress)
            encouragement = _progress_trackers[session_id].get_encouragement_message(progress)

            progress_data = {
                'score': progress['overall_score'],
                'progress_percent': progress['progress_percent'],
                'attempt': progress['attempt_number'],
                'text': progress_text,
                'encouragement': encouragement,
                'is_first': progress.get('is_first', False)
            }

        elapsed = time.time() - start_time
        ctx.log.info(f"✅ Enhanced 분석 완료! ({elapsed:.3f}초)")
        ctx.log.info(f"   Primary 피드백: {len(formatted['primary'])}개")
        ctx.log.info(f"   Workflow 단계: {len([s for s in workflow_steps.values() if s['items']])}개")

        # iOS 친화적 JSON 응답
        return JSONResponse({
            "feedback": {
                "primary": [convert_feedback_to_ios(fb) for fb in formatted['primary']],
                "secondary": [convert_feedback_to_ios(fb) for fb in formatted['secondary']],
                "display_text": display_text,
                "critical_count": formatted['critical_count']
            },
            "workflow": {
                "steps": workflow_steps,
                "text": workflow_text,
                "current_step": get_current_workflow_step(workflow_steps)
            },
            "priorities": {
                "critical": [convert_feedback_to_ios(fb) for fb in priority_groups.get('critical', [])],
                "important": [convert_feedback_to_ios(fb) for fb in priority_groups.get('important', [])],
                "recommended": [convert_feedback_to_ios(fb) for fb in priority_groups.get('recommended', [])]
            },
            "progress": progress_data,
            "processing_time": f"{elapsed:.3f}s",
            "timestamp": time.time()
        })

    except Exception as e:
        ctx.log.error(f"❌ Enhanced 분석 에러: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "error": str(e)
        }, status_code=500)


async def reset_progress(ctx, session_id: str) -> JSONResponse:
    """진행도 초기화"""
    if session_id in _progress_trackers:
        del _progress_trackers[session_id]
        ctx.log.info(f"✅ 진행도 초기화: {session_id}")

    return JSONResponse({
        "status": "reset",
        "session_id": session_id
    })


async def get_recommendations(
    ctx,
    user_path: str,
    top_k: int = 3
) -> JSONResponse:
    """Phase 3.1: AI 레퍼런스 추천"""
    
    if not PHASE_1_3_AVAILABLE:
        return JSONResponse({
            "error": "Recommendations not available"
        }, status_code=503)

    try:
        from analysis.image_analyzer import ImageAnalyzer

        # 사용자 이미지 분석
        analyzer = ImageAnalyzer(user_path)
        features = analyzer.analyze()

        user_cluster = features['cluster']['cluster_id']
        user_embedding = features.get('embedding', None)

        if user_embedding is not None:
            recommender = ReferenceRecommender()
            recommendations = recommender.recommend(
                user_image_path=user_path,
                user_cluster_id=user_cluster,
                user_embedding=user_embedding,
                top_k=top_k
            )

            return JSONResponse({
                "recommendations": recommendations,
                "cluster_id": user_cluster,
                "cluster_label": features['cluster']['cluster_label']
            })
        else:
            return JSONResponse({
                "error": "Could not extract embedding"
            }, status_code=400)

    except Exception as e:
        ctx.log.error(f"❌ 추천 에러: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "error": str(e)
        }, status_code=500)


def extract_user_feedback(comparison: dict) -> list:
    """
    서버에서는 포즈 피드백만 제공
    (프레이밍, 구도는 클라이언트에서 실시간 처리)
    """
    feedback = []

    # 포즈 피드백만 처리 (서버의 주요 역할)
    pose = comparison["pose_comparison"]
    if pose["available"]:
        # 포즈 피드백 안정화를 위해 더 엄격한 조건 적용
        if pose.get("similarity", 0) < 0.8:  # 80% 미만일 때만 피드백
            # 각도 차이 분석
            angle_diffs = pose.get("angle_differences", {})
            position_diffs = pose.get("position_differences", {})

            # 가장 큰 차이가 나는 부분 찾기
            major_issues = []

            for joint, diff in angle_diffs.items():
                if abs(diff) > 15:  # 15도 이상 차이날 때만
                    major_issues.append({
                        "joint": joint,
                        "diff": diff,
                        "type": "angle"
                    })

            # 상위 2개 문제만 피드백
            major_issues.sort(key=lambda x: abs(x["diff"]), reverse=True)

            for i, issue in enumerate(major_issues[:2]):
                if issue["type"] == "angle":
                    joint_name = translate_joint_name(issue["joint"])
                    direction = "더 올리세요" if issue["diff"] > 0 else "더 내리세요"

                    feedback.append({
                        "priority": i + 1,
                        "icon": "👤",
                        "message": f"{joint_name} {direction}",
                        "category": "pose",
                        "currentValue": 0,
                        "targetValue": abs(issue["diff"]),
                        "tolerance": 5,
                        "unit": "도"
                    })

        # 피드백이 있으면 원본 피드백도 추가 (텍스트만)
        elif pose["feedback"]:
            for i, fb in enumerate(pose["feedback"][:2]):
                if "적절합니다" not in fb:
                    feedback.append({
                        "priority": i + 3,
                        "icon": "💡",
                        "message": fb,
                        "category": "pose",
                        "currentValue": None,
                        "targetValue": None,
                        "tolerance": None,
                        "unit": None
                    })

    return feedback[:3]  # 포즈 피드백만 최대 3개


def translate_joint_name(joint: str) -> str:
    """영문 관절명을 한글로 번역"""
    translations = {
        "left_shoulder": "왼쪽 어깨",
        "right_shoulder": "오른쪽 어깨",
        "left_elbow": "왼쪽 팔꿈치",
        "right_elbow": "오른쪽 팔꿈치",
        "left_wrist": "왼쪽 손목",
        "right_wrist": "오른쪽 손목",
        "left_hip": "왼쪽 엉덩이",
        "right_hip": "오른쪽 엉덩이",
        "left_knee": "왼쪽 무릎",
        "right_knee": "오른쪽 무릎",
        "left_ankle": "왼쪽 발목",
        "right_ankle": "오른쪽 발목"
    }
    return translations.get(joint, joint)


def extract_camera_settings(comparison: dict) -> dict:
    """
    카메라에 자동 적용할 설정 값
    (ISO, 화이트밸런스, 노출 보정)
    """
    settings = {}

    # 1. ISO
    exif = comparison["exif_comparison"]
    if exif["available"]:
        ref_iso = exif["ref_settings"].get("iso")
        if ref_iso:
            settings["iso"] = int(ref_iso)

    # 2. 화이트밸런스 (Kelvin)
    color = comparison["color_comparison"]
    ref_temp = color["ref_temperature"]
    wb_map = {
        "cool": 6500,    # 차가운 톤
        "neutral": 5500, # 중성 톤
        "warm": 4500     # 따뜻한 톤
    }
    settings["wbKelvin"] = wb_map.get(ref_temp, 5500)

    # 3. 노출 보정 (EV)
    brightness = comparison["brightness_comparison"]
    settings["evCompensation"] = brightness["ev_adjustment"]

    return settings


def convert_feedback_to_ios(feedback: dict) -> dict:
    """Python 피드백을 iOS 친화적 형식으로 변환"""
    return {
        "priority": feedback.get('priority', 5),
        "category": feedback.get('category', 'general'),
        "message": feedback.get('message', ''),
        "detail": feedback.get('detail', ''),
        "icon": get_category_emoji(feedback.get('category', 'general'))
    }


def get_category_emoji(category: str) -> str:
    """카테고리별 이모지"""
    emoji_map = {
        'pose': '🤸',
        'distance': '📏',
        'brightness': '💡',
        'exposure': '☀️',
        'color': '🎨',
        'saturation': '🌈',
        'white_balance': '⚖️',
        'composition': '📐',
        'framing': '🖼️',
        'blur': '🔍',
        'sharpness': '✨',
        'noise': '📊',
        'style': '🎯',
        'camera_settings': '📷',
        'iso': '📸',
        'aperture': '🔆',
        'backlight': '☀️',
        'lighting_direction': '💡'
    }
    return emoji_map.get(category.lower(), '📋')


def get_current_workflow_step(workflow_steps: dict) -> int:
    """현재 워크플로우 단계 반환 (1-5)"""
    for step_name, step_data in workflow_steps.items():
        if step_data['items']:  # 피드백이 있는 첫 단계
            return step_data['step']
    return 5  # 모두 완료
