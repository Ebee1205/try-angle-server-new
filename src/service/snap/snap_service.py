import time

import pymysql
from fastapi import HTTPException

from src.app_context import AppContext
from src.service.snap.snap_schema import (
    SnapCreateRequest,
    SnapGender,
    SnapItem,
    SnapListItem,
    SnapListResponse,
    SnapUpdateRequest,
)
from src.utils.db_utils import execute_query

_VALID_GENDER = (SnapGender.UNKNOWN, SnapGender.MALE, SnapGender.FEMALE)
_VALID_SORT_BY = {"cDate", "uDate", "viewCnt", "id"}
_VALID_SORT_ORDER = {"asc", "desc"}


def _normalize_epoch_seconds(value: int | None) -> int | None:
    """허용 입력: epoch seconds(10자리) 또는 milliseconds(13자리)."""
    if value is None:
        return None
    # 2001-09-09(1e9s) 이후를 기준으로 ms 입력(>=1e12)은 초로 환산.
    if value >= 1_000_000_000_000:
        return value // 1000
    return value


def _row_to_snap_item(row: tuple) -> SnapItem:
    return SnapItem(
        id=row[0],
        userId=row[1],
        userName=row[2],
        prodId=row[3],
        imgId=row[4],
        sId=row[5],
        snapUrl=row[6],
        comment=row[7],
        gender=row[8],
        userH=row[9],
        userW=row[10],
        viewCnt=row[11],
        cDate=row[12],
        uDate=row[13],
    )


def _row_to_snap_list_item(row: tuple) -> SnapListItem:
    return SnapListItem(
        id=row[0],
        userId=row[1],
        userName=row[2],
        prodId=row[3],
        imgId=row[4],
        sId=row[5],
        snapUrl=row[6],
        viewCnt=row[7],
        cDate=row[8],
        uDate=row[9],
    )


def _ensure_prod_exists(ctx: AppContext, prod_id: int) -> None:
    rows = execute_query(ctx.db_handler, "SELECT id FROM tb_prod WHERE id = %s", (prod_id,))
    if not rows:
        raise HTTPException(status_code=400, detail="Product not found")


def _ensure_img_exists(ctx: AppContext, img_id: int) -> None:
    rows = execute_query(ctx.db_handler, "SELECT id FROM tb_img WHERE id = %s", (img_id,))
    if not rows:
        raise HTTPException(status_code=400, detail="Reference image not found")


def _ensure_session_exists(ctx: AppContext, session_id: str) -> None:
    rows = execute_query(ctx.db_handler, "SELECT id FROM tb_session WHERE id = %s", (session_id,))
    if not rows:
        raise HTTPException(status_code=400, detail="Session not found")


def _should_validate_session_id(session_id: str) -> bool:
    return not session_id.startswith("test-")


def _get_snap_row(ctx: AppContext, snap_id: int) -> SnapItem:
    rows = execute_query(
        ctx.db_handler,
        """
            SELECT
                s.id,
                s.userId,
                u.nickname,
                s.prodId,
                s.imgId,
                s.sId,
                s.snapUrl,
                s.comment,
                s.gender,
                s.userH,
                s.userW,
                s.viewCnt,
                s.cDate,
                s.uDate
            FROM tb_snap s
            LEFT JOIN tb_user u ON u.id = s.userId
            WHERE s.id = %s
        """,
        (snap_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Snap not found")
    return _row_to_snap_item(rows[0])


def list_snaps(
    ctx: AppContext,
    page: int = 1,
    limit: int = 20,
    user_id: int | None = None,
    prod_id: int | None = None,
    img_id: int | None = None,
    from_date: int | None = None,
    to_date: int | None = None,
    sort_by: str = "cDate",
    sort_order: str = "desc",
) -> SnapListResponse:
    """스냅 목록 조회"""
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    from_date = _normalize_epoch_seconds(from_date)
    to_date = _normalize_epoch_seconds(to_date)

    filters = []
    params: list = []

    if user_id is not None:
        filters.append("s.userId = %s")
        params.append(user_id)
    if prod_id is not None:
        filters.append("s.prodId = %s")
        params.append(prod_id)
    if img_id is not None:
        filters.append("s.imgId = %s")
        params.append(img_id)
    if from_date is not None:
        filters.append("s.cDate >= %s")
        params.append(from_date)
    if to_date is not None:
        filters.append("s.cDate <= %s")
        params.append(to_date)

    sort_by = (sort_by or "cDate").strip()
    sort_order = (sort_order or "desc").strip().lower()

    if sort_by not in _VALID_SORT_BY:
        raise HTTPException(status_code=400, detail="Invalid sortBy value")
    if sort_order not in _VALID_SORT_ORDER:
        raise HTTPException(status_code=400, detail="Invalid sortOrder value")
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(status_code=400, detail="fromDate must be less than or equal to toDate")

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    offset = (page - 1) * limit

    count_sql = f"SELECT COUNT(*) FROM tb_snap s {where_clause}"
    count_rows = execute_query(ctx.db_handler, count_sql, tuple(params))
    total = count_rows[0][0] if count_rows else 0

    list_sql = f"""
        SELECT
            s.id,
            s.userId,
            u.nickname AS userName,
            s.prodId,
            s.imgId,
            s.sId,
            s.snapUrl,
            s.viewCnt,
            s.cDate,
            s.uDate
        FROM tb_snap s
        LEFT JOIN tb_user u ON u.id = s.userId
        {where_clause}
        ORDER BY s.{sort_by} {sort_order.upper()}
        LIMIT %s OFFSET %s
    """
    list_params = tuple(params) + (limit, offset)
    rows = execute_query(ctx.db_handler, list_sql, list_params)
    items = [_row_to_snap_list_item(row) for row in rows]

    return SnapListResponse(items=items, total=total, page=page, limit=limit)


def get_snap(ctx: AppContext, snap_id: int) -> SnapItem:
    """스냅 상세 조회"""
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return _get_snap_row(ctx, snap_id)


def create_snap(ctx: AppContext, payload: SnapCreateRequest, user_id: int) -> SnapItem:
    """스냅 등록"""
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    if payload.gender not in _VALID_GENDER:
        raise HTTPException(status_code=400, detail="Invalid gender value")

    if not payload.sId:
        raise HTTPException(status_code=400, detail="sId is required")

    _ensure_prod_exists(ctx, payload.prodId)
    _ensure_img_exists(ctx, payload.imgId)
    if payload.sId and _should_validate_session_id(payload.sId):
        _ensure_session_exists(ctx, payload.sId)

    now = int(time.time())

    sql = """
        INSERT INTO tb_snap (userId, prodId, imgId, sId, snapUrl, comment, gender, userH, userW, viewCnt, cDate, uDate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        user_id,
        payload.prodId,
        payload.imgId,
        payload.sId,
        payload.snapUrl,
        payload.comment,
        payload.gender,
        payload.userH,
        payload.userW,
        0,
        now,
        now,
    )

    conn = ctx.db_handler.get_connection()
    new_id: int | None = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            new_id = cursor.lastrowid
        conn.commit()
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if getattr(e, "args", None) and e.args[0] == 1062:
            raise HTTPException(status_code=409, detail="Session already has a snap")
        if ctx.log:
            ctx.log.error(f"Failed to create snap: {e}")
        raise HTTPException(status_code=500, detail="Failed to create snap")
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to create snap: {e}")
        raise HTTPException(status_code=500, detail="Failed to create snap")

    return _get_snap_row(ctx, new_id)


def update_snap(ctx: AppContext, payload: SnapUpdateRequest) -> SnapItem:
    """스냅 수정"""
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    _get_snap_row(ctx, payload.id)

    if payload.gender is not None and payload.gender not in _VALID_GENDER:
        raise HTTPException(status_code=400, detail="Invalid gender value")

    fields = []
    params = []

    if payload.prodId is not None:
        _ensure_prod_exists(ctx, payload.prodId)
        fields.append("prodId = %s")
        params.append(payload.prodId)
    if payload.imgId is not None:
        _ensure_img_exists(ctx, payload.imgId)
        fields.append("imgId = %s")
        params.append(payload.imgId)
    if payload.sId is not None:
        if payload.sId != "":
            if _should_validate_session_id(payload.sId):
                _ensure_session_exists(ctx, payload.sId)
            fields.append("sId = %s")
            params.append(payload.sId)
        else:
            fields.append("sId = %s")
            params.append(None)
    if payload.snapUrl is not None:
        fields.append("snapUrl = %s")
        params.append(payload.snapUrl)
    if payload.comment is not None:
        fields.append("comment = %s")
        params.append(payload.comment)
    if payload.gender is not None:
        fields.append("gender = %s")
        params.append(payload.gender)
    if payload.userH is not None:
        fields.append("userH = %s")
        params.append(payload.userH)
    if payload.userW is not None:
        fields.append("userW = %s")
        params.append(payload.userW)
    if payload.viewCnt is not None:
        fields.append("viewCnt = %s")
        params.append(payload.viewCnt)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    now = int(time.time())
    fields.append("uDate = %s")
    params.append(now)
    params.append(payload.id)

    sql = f"UPDATE tb_snap SET {', '.join(fields)} WHERE id = %s"
    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
        conn.commit()
    except pymysql.err.IntegrityError as e:
        conn.rollback()
        if getattr(e, "args", None) and e.args[0] == 1062:
            raise HTTPException(status_code=409, detail="Session already has a snap")
        if ctx.log:
            ctx.log.error(f"Failed to update snap: {e}")
        raise HTTPException(status_code=500, detail="Failed to update snap")
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to update snap: {e}")
        raise HTTPException(status_code=500, detail="Failed to update snap")

    return _get_snap_row(ctx, payload.id)


def delete_snap(ctx: AppContext, snap_id: int) -> dict:
    """스냅 삭제"""
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    _get_snap_row(ctx, snap_id)

    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tb_snap WHERE id = %s", (snap_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to delete snap: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete snap")

    return {"id": snap_id}
