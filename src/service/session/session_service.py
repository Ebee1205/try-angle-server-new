import json
import time

import pymysql
from fastapi import HTTPException

from src.app_context import AppContext
from src.core.id_generator import generate_sid
from src.service.auth.auth_schema import UserRole
from src.service.session.session_schema import (
    SessionDetailResponse,
    SessionEndRequest,
    SessionItem,
    SessionListResponse,
    SessionStartRequest,
    SessionStatus,
)
from src.utils.db_utils import execute_query


_Q = {
    "SR": """
            SELECT
                s.id,
                s.userId,
                u.nickname AS userName,
                s.imgId,
                s.sDate,
                s.eDate,
                s.device,
                s.sStat,
                s.cDate,
                s.uDate
            FROM tb_session s
            LEFT JOIN tb_user u ON u.id = s.userId
            WHERE s.id = %s
        """,
    "LB": """
        SELECT
            s.id, s.userId, u.nickname AS userName, s.imgId,
            s.sDate, s.eDate, s.device, s.sStat, s.cDate, s.uDate
        FROM tb_session s
        LEFT JOIN tb_user u ON s.userId = u.id
        WHERE 1=1
    """,
    "LC": """
        SELECT COUNT(DISTINCT s.id)
        FROM tb_session s
        LEFT JOIN tb_user u ON s.userId = u.id
        WHERE 1=1
    """,
    "SI": """
        INSERT INTO tb_session (id, userId, imgId, sDate, eDate, device, sStat, cDate, uDate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    "SU": """
        UPDATE tb_session
        SET eDate = %s,
            sStat = %s,
            uDate = %s
        WHERE id = %s
    """,
}


_W = {
    "user": "AND s.userId = %s",
    "img": "AND s.imgId = %s",
    "stat": "AND s.sStat = %s",
    "sdate": "AND s.sDate >= %s",
    "edate": "AND s.sDate <= %s",
}


def _parse_json_field(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None


def _row_to_session_item(row: tuple) -> SessionItem:
    return SessionItem(
        id=row[0],
        userId=row[1],
        userName=row[2],
        imgId=row[3],
        sDate=row[4],
        eDate=row[5],
        device=_parse_json_field(row[6]),
        sStat=row[7],
        cDate=row[8],
        uDate=row[9],
    )


def _get_session_row(ctx: AppContext, session_id: str) -> SessionItem:
    rows = execute_query(ctx.db_handler, _Q["SR"], (session_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")
    return _row_to_session_item(rows[0])


def _is_admin_role(user_role: str | UserRole | None) -> bool:
    return user_role in (UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value)


def _get_owned_session_row(
    ctx: AppContext,
    session_id: str,
    user_id: int,
    user_role: str | UserRole | None = None,
) -> SessionItem:
    session = _get_session_row(ctx, session_id)
    if _is_admin_role(user_role):
        return session
    if session.userId != user_id:
        raise HTTPException(status_code=403, detail="Session access denied")
    return session


def list_sessions(
    ctx: AppContext,
    page: int = 1,
    limit: int = 20,
    user_id: int = None,
    img_id: int = None,
    s_stat: int = None,
    sDate: int = None,
    eDate: int = None,
) -> SessionListResponse:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    offset = (page - 1) * limit
    where_clauses: list[str] = []
    base_params: list[int] = []

    for k, v in (
        ("user", user_id),
        ("img", img_id),
        ("stat", s_stat),
        ("sdate", sDate),
        ("edate", eDate),
    ):
        if v is None:
            continue
        where_clauses.append(_W[k])
        base_params.append(v)

    where_str = " ".join(where_clauses)
    count_res = execute_query(ctx.db_handler, f"{_Q['LC']} {where_str}", tuple(base_params))
    total = count_res[0][0] if count_res else 0
    rows = execute_query(
        ctx.db_handler,
        f"{_Q['LB']} {where_str} ORDER BY s.sDate DESC LIMIT %s OFFSET %s",
        tuple(base_params + [limit, offset]),
    )

    items = [_row_to_session_item(row) for row in rows]

    return SessionListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )

def get_session_detail(
    ctx: AppContext,
    session_id: str,
    user_id: int,
    user_role: str | UserRole | None = None,
) -> SessionDetailResponse:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    session = _get_owned_session_row(ctx, session_id, user_id, user_role=user_role)

    return SessionDetailResponse(session=session)


def start_session(ctx: AppContext, payload: SessionStartRequest, user_id: int) -> SessionItem:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    img_rows = execute_query(ctx.db_handler, "SELECT id FROM tb_img WHERE id = %s", (payload.imgId,))
    if not img_rows:
        raise HTTPException(status_code=404, detail="Reference image not found")

    now = int(time.time())
    device_json = json.dumps(payload.device, ensure_ascii=False) if payload.device is not None else None

    conn = ctx.db_handler.get_connection()
    for _ in range(5):
        session_id = generate_sid()
        try:
            params = (
                session_id,
                user_id,
                payload.imgId,
                now,
                None,
                device_json,
                SessionStatus.READY.value,
                now,
                now,
            )
            with conn.cursor() as cursor:
                cursor.execute(_Q["SI"], params)
            conn.commit()
            return _get_session_row(ctx, session_id)
        except pymysql.err.IntegrityError as e:
            conn.rollback()
            if getattr(e, "args", None) and e.args[0] == 1062:
                continue
            if ctx.log:
                ctx.log.error(f"Failed to start session: {e}")
            raise HTTPException(status_code=500, detail="Failed to start session")
        except Exception as e:
            conn.rollback()
            if ctx.log:
                ctx.log.error(f"Failed to start session: {e}")
            raise HTTPException(status_code=500, detail="Failed to start session")

    raise HTTPException(status_code=503, detail="Could not allocate unique session ID")


def end_session(ctx: AppContext, payload: SessionEndRequest) -> SessionItem:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    current = _get_session_row(ctx, payload.id)
    if current.sStat != SessionStatus.READY.value:
        raise HTTPException(status_code=409, detail="Session already closed")

    now = int(time.time())
    params = (now, SessionStatus.COMPLETED.value, now, payload.id)

    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(_Q["SU"], params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to end session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end session")

    return _get_session_row(ctx, payload.id)