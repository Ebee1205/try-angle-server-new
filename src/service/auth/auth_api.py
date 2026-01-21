from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

import src.common.common_codes as codes
from src.service.auth import auth_service
from src.service.auth.auth_schema import UserCreate, UserResponse, Token, UserLogin

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# OAuth2 scheme for Swagger UI auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

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
    user = auth_service.authenticate_user(ctx, login_req.emailAddress, login_req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        ctx, 
        data={"sub": user["emailAddress"], "role": user["role"]}
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
        data={"sub": user["emailAddress"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(request: Request, token: str = Depends(oauth2_scheme)):
    """
    현재 사용자 정보 조회
    """
    # 여기서 토큰 검증 로직이 필요함. 
    # 실제로는 common dependency 등으로 분리하는 것이 좋음.
    ctx = request.app.state.ctx
    # For now, just decode and find (simplification)
    import jwt
    try:
        payload = jwt.decode(token, ctx.cfg.secret_key, algorithms=[auth_service.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
             raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
        
    user = auth_service.get_user_by_email(ctx, email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user
