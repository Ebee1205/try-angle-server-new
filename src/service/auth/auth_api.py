from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

import src.common.common_codes as codes
from src.service.auth import auth_service
from src.service.auth.auth_schema import UserCreate, UserResponse, Token, UserLogin
from src.service.auth.jwt_auth import require_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse, status_code=201)
async def signup(request: Request, user: UserCreate):
    """
    회원가입 API
    """
    ctx = request.app.state.ctx
    
    # 비밀번호 확인 체크
    if user.password and user.passwordCheck:
        if user.password != user.passwordCheck:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password match failed"
            )

    new_user = auth_service.create_user(ctx, user)
    return new_user

@router.post("/login", response_model=Token)
async def login(request: Request, login_req: UserLogin):
    """
    로그인 API (JSON Body)
    """
    ctx = request.app.state.ctx
    user = auth_service.authenticate_user(ctx, login_req.email, login_req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        ctx, 
        data={"sub": user["email"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_form(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Swagger UI용 로그인 API (Form Data)
    """
    ctx = request.app.state.ctx
    user = auth_service.authenticate_user(ctx, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        ctx, 
        data={"sub": user["email"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(request: Request, user=Depends(require_user)):
    """
    현재 사용자 정보 조회 (JWT 인증)
    """
    return user
