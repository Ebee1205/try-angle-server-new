import json
import time

import pymysql
from fastapi import HTTPException

from src.app_context import AppContext
from src.core.id_generator import generate_sid
from src.service.session.session_schema import SessionEndRequest, SessionItem, SessionStartRequest, SessionStatus
from src.utils.db_utils import execute_query


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
        imgId=row[2],
        sDate=row[3],
        eDate=row[4],
        device=_parse_json_field(row[5]),
        sStat=row[6],
        cDate=row[7],
        uDate=row[8],
    )


def _get_session_row(ctx: AppContext, session_id: str) -> SessionItem:
    rows = execute_query(
        ctx.db_handler,
        """
            SELECT id, userId, imgId, sDate, eDate, device, sStat, cDate, uDate
            FROM tb_session
            WHERE id = %s
        """,
        (session_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Session not found")
    return _row_to_session_item(rows[0])


def start_session(ctx: AppContext, payload: SessionStartRequest, user_id: int) -> SessionItem:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    img_rows = execute_query(ctx.db_handler, "SELECT id FROM tb_img WHERE id = %s", (payload.imgId,))
    if not img_rows:
        raise HTTPException(status_code=404, detail="Reference image not found")

    now = int(time.time())
    device_json = json.dumps(payload.device, ensure_ascii=False) if payload.device is not None else None

    sql = """
        INSERT INTO tb_session (id, userId, imgId, sDate, eDate, device, sStat, cDate, uDate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

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
                cursor.execute(sql, params)
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
    sql = """
        UPDATE tb_session
        SET eDate = %s,
            sStat = %s,
            uDate = %s
        WHERE id = %s
    """
    params = (now, SessionStatus.COMPLETED.value, now, payload.id)

    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to end session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end session")

    return _get_session_row(ctx, payload.id)