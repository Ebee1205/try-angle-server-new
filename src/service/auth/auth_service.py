from datetime import datetime, timedelta
from typing import Optional
import jwt  # Using PyJWT or python-jose
from fastapi import HTTPException, status
from passlib.context import CryptContext

from src.app_context import AppContext
from src.utils.db_utils import execute_query
from src.service.auth.auth_schema import UserCreate, UserRole, TokenData, UserResponse

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(ctx: AppContext, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration from config
        expire_minutes = getattr(ctx.cfg, "access_token_expire_minutes", 60)
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire})
    secret_key = ctx.cfg.secret_key
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(ctx: AppContext, email: str) -> Optional[dict]:
    # DB에서 사용자 조회
    sql = """
        SELECT id, email, password, name, nickname, phone,
               emailConf, `desc`, fileId, role, extra
        FROM tb_user
        WHERE email = %s
    """
    if not ctx.db_handler:
        return None

    rows = execute_query(ctx.db_handler, sql, (email,))
    if rows:
        row = rows[0]
        extra = row[10] or {}
        if isinstance(extra, str):
            import json as _json
            extra = _json.loads(extra)
        return {
            "id": row[0],
            "emailAddress": row[1],
            "password": row[2],
            "name": row[3],
            "nickname": row[4],
            "phoneNumber": row[5],
            "emailConfirm": row[6],
            "description": row[7],
            "fileId": row[8],
            "role": row[9],
            "extra": extra,
            "provider": extra.get("provider", "email"),
            "providerId": extra.get("providerId"),
        }
    return None

def create_user(ctx: AppContext, user: UserCreate) -> dict:
    if ctx.db_handler is None:
         # DB 연결이 없을 경우 에러 처리 혹은 Mocking
        raise HTTPException(status_code=500, detail="Database not initialized")

    existing = get_user_by_email(ctx, user.emailAddress)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password) if user.password else None

    # role 기본값 확인
    role = user.role if user.role else UserRole.CLIENT

    # provider/providerId는 extra JSON에 저장
    import json as _json
    import time as _time
    from src.common.id_generator import generate_task_id

    extra = dict(user.extra) if user.extra else {}
    if user.provider and user.provider != "email":
        extra["provider"] = user.provider
    if user.providerId:
        extra["providerId"] = user.providerId

    now = int(_time.time())
    new_id = f"usr_{generate_task_id().replace('-', '')[:16]}"

    sql = """
        INSERT INTO tb_user (
            id, name, nickname, email, password, phone,
            emailConf, `desc`, fileId, role, extra, cDate, uDate
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        new_id, user.name, user.nickname, user.emailAddress, hashed_password,
        user.phoneNumber, user.emailConfirm, user.description, user.fileId,
        role.value, _json.dumps(extra, ensure_ascii=False), now, now
    )

    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
    except Exception as e:
        conn.rollback()
        ctx.log.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {
        "id": new_id,
        "emailAddress": user.emailAddress,
        "name": user.name,
        "nickname": user.nickname,
        "role": role,
        "provider": user.provider,
    }

def authenticate_user(ctx: AppContext, email: str, password: str):
    user = get_user_by_email(ctx, email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user
