import time

from fastapi import HTTPException

from src.app_context import AppContext
from src.utils.db_utils import execute_query
from src.service.ctg.ctg_schema import (
    CtgCreateRequest,
    CtgItem,
    CtgListResponse,
    CtgUpdateRequest,
)


def _row_to_ctg_item(row: tuple) -> CtgItem:
    return CtgItem(id=row[0], name=row[1], cDate=row[2], uDate=row[3])


def list_ctgs(ctx: AppContext, page: int = 1, limit: int = 20) -> CtgListResponse:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    count_rows = execute_query(ctx.db_handler, "SELECT COUNT(*) FROM tb_img_ctg", ())
    total = count_rows[0][0] if count_rows else 0

    if page == 0:
        rows = execute_query(
            ctx.db_handler,
            "SELECT id, name, cDate, uDate FROM tb_img_ctg ORDER BY cDate ASC",
            (),
        )
    else:
        offset = (page - 1) * limit
        rows = execute_query(
            ctx.db_handler,
            "SELECT id, name, cDate, uDate FROM tb_img_ctg ORDER BY cDate ASC LIMIT %s OFFSET %s",
            (limit, offset),
        )
    items = [_row_to_ctg_item(row) for row in rows]
    return CtgListResponse(items=items, total=total, page=page, limit=limit)


def get_ctg(ctx: AppContext, ctg_id: int) -> CtgItem:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    rows = execute_query(ctx.db_handler, "SELECT id, name, cDate, uDate FROM tb_img_ctg WHERE id = %s", (ctg_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Category not found")
    return _row_to_ctg_item(rows[0])


def create_ctg(ctx: AppContext, payload: CtgCreateRequest) -> CtgItem:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    # name 중복 체크
    dup = execute_query(ctx.db_handler, "SELECT id FROM tb_img_ctg WHERE name = %s", (payload.name,))
    if dup:
        raise HTTPException(status_code=400, detail="Category name already exists")

    now = int(time.time())

    sql = "INSERT INTO tb_img_ctg (name, cDate, uDate) VALUES (%s, %s, %s)"
    params = (payload.name, now, now)

    conn = ctx.db_handler.get_connection()
    new_id: int | None = None
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            new_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to create category: {e}")
        raise HTTPException(status_code=500, detail="Failed to create category")

    return CtgItem(id=new_id, name=payload.name, cDate=now, uDate=now)


def update_ctg(ctx: AppContext, payload: CtgUpdateRequest) -> CtgItem:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    rows = execute_query(ctx.db_handler, "SELECT id, name, cDate, uDate FROM tb_img_ctg WHERE id = %s", (payload.id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Category not found")

    fields = []
    params = []
    if payload.name is not None:
        fields.append("name = %s")
        params.append(payload.name)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    now = int(time.time())
    fields.append("uDate = %s")
    params.append(now)
    params.append(payload.id)

    sql = f"UPDATE tb_img_ctg SET {', '.join(fields)} WHERE id = %s"
    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to update category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")

    updated = execute_query(ctx.db_handler, "SELECT id, name, cDate, uDate FROM tb_img_ctg WHERE id = %s", (payload.id,))
    return _row_to_ctg_item(updated[0])


def delete_ctg(ctx: AppContext, ctg_id: int) -> dict:
    if not ctx.db_handler:
        raise HTTPException(status_code=500, detail="Database not initialized")

    rows = execute_query(ctx.db_handler, "SELECT id FROM tb_img_ctg WHERE id = %s", (ctg_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Category not found")

    conn = ctx.db_handler.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tb_img_ctg WHERE id = %s", (ctg_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        if ctx.log:
            ctx.log.error(f"Failed to delete category: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete category")

    return {"id": ctg_id, "deleted": True}
