from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class UserBase(BaseModel):
    """
    사용자 기본 정보 스키마
    """
    name: str = Field(..., description="이름")
    nickname: Optional[str] = Field(None, description="별명")
    emailAddress: EmailStr = Field(..., description="이메일")
    phoneNumber: Optional[str] = Field(None, description="핸드폰번호")
    emailConfirm: str = Field("2", description="메일 주소 확인 여부 1: yes 2: no")
    description: Optional[str] = Field(None, description="설명")
    fileId: Optional[str] = Field(None, description="프로필 파일 아이디")
    extra: Dict[str, Any] = Field(default_factory=dict, description="부가정보")

    # 간편 로그인(Social Login) 확장을 위한 필드
    provider: str = Field("email", description="가입 경로 (email, google, naver, kakao 등)")
    providerId: Optional[str] = Field(None, description="소셜 로그인 제공자 측의 식별자")


class UserCreate(UserBase):
    """
    회원가입 요청 스키마
    """
    password: Optional[str] = Field(None, description="비밀번호 (이메일 가입 시 필수, 소셜 로그인 시 선택)")
    passwordCheck: Optional[str] = Field(None, description="비밀번호 확인")
    agreeTerms: bool = Field(True, description="약관 동의 여부")


class UserUpdate(BaseModel):
    """
    회원정보 수정 요청 스키마
    - 변경할 필드만 전달
    """
    name: Optional[str] = None
    nickname: Optional[str] = None
    phoneNumber: Optional[str] = None
    description: Optional[str] = None
    fileId: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class UserLogin(BaseModel):
    """
    이메일 로그인 요청 스키마
    """
    emailAddress: EmailStr
    password: str


class SocialLoginRequest(BaseModel):
    """
    소셜 로그인 요청 스키마 (예시)
    """
    provider: str
    token: str  # 클라이언트에서 받은 액세스 토큰 등


class UserResponse(UserBase):
    """
    회원정보 응답 스키마
    """
    id: str
    # password는 제외됨

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
