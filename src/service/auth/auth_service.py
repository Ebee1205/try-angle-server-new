from datetime import datetime, timedelta
from typing import Optional
import hashlib
import jwt  # Using PyJWT or python-jose
from fastapi import HTTPException, status
from passlib.context import CryptContext

from src.app_context import AppContext
from src.utils.db_utils import execute_query
from src.service.auth.auth_schema import UserCreate, UserRole, TokenData, UserResponse

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
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
        SELECT id, emailAddress, password, name, nickname, phoneNumber, 
               emailConfirm, description, fileId, role, provider, providerId, extra
        FROM users
        WHERE emailAddress = %s
    """
    if not ctx.db_handler:
        # DB 핸들러가 없으면 (테스트용) None 리턴하거나 임시 처리
        return None
        
    rows = execute_query(ctx.db_handler, sql, (email,))
    if rows:
        # tuple/list result -> dict conversion needs to be handled if fetchall returns tuples
        # Assuming fetchall returns dictionaries or we map it.
        # Check db_handler implementation. usually pymysql cursors return tuples by default unless DictCursor is used.
        # Let's assume standard tuple and map it manually for safety or use DictCursor in db_handler.
        # For now, I'll map based on the select order.
        row = rows[0]
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
            "provider": row[10],
            "providerId": row[11],
            "extra": row[12] if len(row) > 12 else {} # JSON parsing needed if it's a string
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

    sql = """
        INSERT INTO users (
            name, nickname, emailAddress, password, phoneNumber, 
            emailConfirm, description, fileId, role, provider, providerId
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        user.name, user.nickname, user.emailAddress, hashed_password, user.phoneNumber,
        user.emailConfirm, user.description, user.fileId, role.value, user.provider, user.providerId
    )
    
    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            new_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        ctx.log.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Created user object
    return {
        "id": str(new_id),
        "emailAddress": user.emailAddress,
        "name": user.name,
        "nickname": user.nickname,
        "role": role,
        "provider": user.provider
    }

def authenticate_user(ctx: AppContext, email: str, password: str):
    user = get_user_by_email(ctx, email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user
