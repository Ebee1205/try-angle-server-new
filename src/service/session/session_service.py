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
        maxStuckSec=row[10] if len(row) > 10 else None,
        snapshotCount=row[11] if len(row) > 11 else None,
        mainFeedback=row[12] if len(row) > 12 else None,
    )


def _get_session_row(ctx: AppContext, session_id: str) -> SessionItem:
    rows = execute_query(
        ctx.db_handler,
        """
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
        (session_id,),
    )
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
    category: str = None,      
    feedback: str = None,      
    stuckSec: int = None,      
    canCapture: str = None,    
) -> SessionListResponse:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    offset = (page - 1) * limit

    # 1. Base Query 선언 (집계 서브쿼리 포함)
    base_sql = """
        SELECT
            s.id, s.userId, u.nickname AS userName, s.imgId,
            s.sDate, s.eDate, s.device, s.sStat, s.cDate, s.uDate,
            (SELECT MAX(rt.stuckSec) FROM tb_rt_snapshot rt WHERE rt.sId = s.id) AS maxStuckSec,
            (SELECT COUNT(*) FROM tb_rt_snapshot rt WHERE rt.sId = s.id) AS snapshotCount,
            (SELECT rt.feedback FROM tb_rt_snapshot rt WHERE rt.sId = s.id ORDER BY rt.secSeq DESC LIMIT 1) AS mainFeedback
        FROM tb_session s
        LEFT JOIN tb_user u ON s.userId = u.id
        WHERE 1=1
    """
    
    # count 쿼리는 집계 필드 제외 (count만 필요)
    count_sql = """
        SELECT COUNT(DISTINCT s.id)
        FROM tb_session s
        LEFT JOIN tb_user u ON s.userId = u.id
        WHERE 1=1
    """

    # count용 파라미터와 list용 파라미터를 완전히 독립적으로 관리하여 꼬임 방지
    where_clauses = []
    base_params = []

    # 기존 기본 필터링 조건 추가
    if user_id is not None:
        where_clauses.append("AND s.userId = %s")
        base_params.append(user_id)
    if img_id is not None:
        where_clauses.append("AND s.imgId = %s")
        base_params.append(img_id)
    if s_stat is not None:
        where_clauses.append("AND s.sStat = %s")
        base_params.append(s_stat)
    if sDate is not None:
        where_clauses.append("AND s.sDate >= %s")
        base_params.append(sDate)
    if eDate is not None:
        where_clauses.append("AND s.sDate <= %s")
        base_params.append(eDate)

    # 실시간 스냅샷 필터링 (필터가 있을 때만 동적으로 조인 처리)
    # stuckSec >= 0은 항상 참이므로, stuckSec > 0일 때만 필터 적용
    if any(v is not None for v in [category, feedback, canCapture]) or (stuckSec is not None and stuckSec > 0):
        sub_clauses = ["rt.sId = s.id"]
        
        if category is not None:
            sub_clauses.append("rt.category = %s")
            base_params.append(category)
        if feedback is not None:
            sub_clauses.append("rt.feedback LIKE %s")
            base_params.append(f"%{feedback}%")
        if stuckSec is not None and stuckSec > 0:
            sub_clauses.append("rt.stuckSec >= %s")
            base_params.append(stuckSec)
        if canCapture is not None:
            sub_clauses.append("rt.canCapture = %s")
            base_params.append(canCapture)
            
        sub_query = f"AND EXISTS (SELECT 1 FROM tb_rt_snapshot rt WHERE {' AND '.join(sub_clauses)})"
        where_clauses.append(sub_query)

    # 모든 조건절 결합
    where_str = " ".join(where_clauses)
    
    # 2. 전체 건수(Total Count) 조회
    final_count_sql = f"{count_sql} {where_str}"
    # count용 쿼리에는 오직 순수 검색 파라미터(base_params)만 바인딩
    count_res = execute_query(ctx.db_handler, final_count_sql, tuple(base_params))
    total = count_res[0][0] if count_res else 0

    # 3. 페이징 데이터 조회
    final_list_sql = f"{base_sql} {where_str} ORDER BY s.sDate DESC LIMIT %s OFFSET %s"
    # list용 쿼리에는 검색 파라미터 뒤에 [LIMIT, OFFSET]을 정확히 붙여서 전달
    list_params = base_params + [limit, offset]
    
    rows = execute_query(ctx.db_handler, final_list_sql, tuple(list_params))

    # 4. 엔티티 변환 및 결과 반환
    items = [_row_to_session_item(row) for row in rows]

    return SessionListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit
    )

def _extract_records(raw_payload) -> list[dict]:
    payload = _parse_json_field(raw_payload)
    if not isinstance(payload, dict):
        return []
    records = payload.get("records")
    if not isinstance(records, list):
        return []
    return [record for record in records if isinstance(record, dict)]


def get_session_detail(
    ctx: AppContext,
    session_id: str,
    user_id: int,
    user_role: str | UserRole | None = None,
    from_sec_seq: int | None = None,
    to_sec_seq: int | None = None,
) -> SessionDetailResponse:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    session = _get_owned_session_row(ctx, session_id, user_id, user_role=user_role)

    where_parts = ["sId = %s"]
    params: list = [session_id]

    if from_sec_seq is not None:
        where_parts.append("secSeq >= %s")
        params.append(from_sec_seq)
    if to_sec_seq is not None:
        where_parts.append("secSeq <= %s")
        params.append(to_sec_seq)

    where_clause = " AND ".join(where_parts)
    rows = execute_query(
        ctx.db_handler,
        f"""
            SELECT secSeq, sDate, eDate, rawPayload, cDate
            FROM tb_rt_snapshot
            WHERE {where_clause}
            ORDER BY secSeq ASC
        """,
        tuple(params),
    )

    # Flatten records from each sec-row into a single snapshots list of record objects
    snapshots: list[dict] = []
    record_count = 0
    for row in rows:
        records = _extract_records(row[3])
        for rec in records:
            # Ensure keys exist and map to expected output fields
            snapshot_rec = {
                "tid": rec.get("tid"),
                "fseq": rec.get("fseq"),
                "gate": rec.get("gate"),
                "offsetMs": rec.get("offsetMs"),
                "cur": rec.get("cur"),
                "res": rec.get("res"),
            }
            snapshots.append(snapshot_rec)
        record_count += len(records)

    return SessionDetailResponse(
        session=session,
        snapshots=snapshots,
        secCount=len(rows),
        recordCount=record_count,
    )


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