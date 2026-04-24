"""
임시 정적 토큰 인증 모듈

DB 캐시가 없는 환경에서 사용하는 임시 정적 토큰입니다.
실제 서비스 배포 전에 JWT 기반 인증으로 교체해야 합니다.

토큰 목록:
  SUPER_ADMIN : static-token-super-admin-tryangle
  ADMIN       : static-token-admin-tryangle
  CLIENT      : static-token-user-tryangle
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.service.auth.auth_schema import UserRole

# ── 정적 토큰 테이블 ──────────────────────────────────────────────────────────
STATIC_TOKENS: dict[str, UserRole] = {
    "static-token-super-admin-tryangle": UserRole.SUPER_ADMIN,
    "static-token-admin-tryangle":       UserRole.ADMIN,
    "static-token-user-tryangle":        UserRole.CLIENT,
}

# ── Bearer 스키마 (Swagger UI 자물쇠 버튼 지원) ───────────────────────────────
_bearer = HTTPBearer(auto_error=True)


def get_current_role(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UserRole:
    """Authorization: Bearer <token> 헤더를 검증하고 역할(UserRole)을 반환합니다."""
    token = credentials.credentials
    role = STATIC_TOKENS.get(token)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return role


def require_user(role: UserRole = Depends(get_current_role)) -> UserRole:
    """CLIENT 이상의 모든 역할 허용 (기본 인증)"""
    return role


def require_admin(role: UserRole = Depends(get_current_role)) -> UserRole:
    """ADMIN 또는 SUPER_ADMIN 역할만 허용"""
    if role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privilege required",
        )
    return role


def require_super_admin(role: UserRole = Depends(get_current_role)) -> UserRole:
    """SUPER_ADMIN 역할만 허용"""
    if role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privilege required",
        )
    return role
